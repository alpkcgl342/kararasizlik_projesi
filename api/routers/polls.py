"""`/api/polls/*` — anket oluşturma, listeleme, detay ve oylama."""
from uuid import UUID, uuid4

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from api.config import get_settings
from api.database import get_session
from api.deps import get_current_user, get_current_user_optional
from api.models import Poll, PollOption, User, Vote
from api.schemas import PollCreate, PollDetail, PollListItem, PollOptionRead, VoteRequest

router = APIRouter(prefix="/api/polls", tags=["polls"])
settings = get_settings()

GUEST_ID_COOKIE_NAME = "guest_id"
GUEST_ID_MAX_AGE_SECONDS = 60 * 60 * 24 * 365  # 1 yıl


def _get_poll_or_404(session: Session, poll_id: int) -> Poll:
    poll = session.get(Poll, poll_id)
    if poll is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anket bulunamadı")
    return poll


def _serialize_poll(
    session: Session,
    poll: Poll,
    voter_user_id: int | None,
    voter_guest_id: UUID | None,
) -> PollDetail:
    creator = session.get(User, poll.created_by_id)
    options = session.exec(
        select(PollOption).where(PollOption.poll_id == poll.id).order_by(PollOption.order)
    ).all()

    counts = dict(
        session.exec(
            select(Vote.option_id, func.count())
            .where(Vote.poll_id == poll.id)
            .group_by(Vote.option_id)
        ).all()
    )
    total_votes = sum(counts.values())

    option_reads = [
        PollOptionRead(
            id=option.id,
            text=option.text,
            votes=counts.get(option.id, 0),
            percentage=round(counts.get(option.id, 0) / total_votes * 100, 1) if total_votes else 0.0,
        )
        for option in options
    ]

    voted_option_id = None
    if voter_user_id is not None:
        vote = session.exec(
            select(Vote).where(Vote.poll_id == poll.id, Vote.user_id == voter_user_id)
        ).first()
        voted_option_id = vote.option_id if vote else None
    if voted_option_id is None and voter_guest_id is not None:
        # Üye girişi yapılmış olsa bile, aynı tarayıcıda daha önce misafir olarak
        # kullanılmış bir oy varsa "zaten oy kullandı" durumunu doğru yansıt.
        vote = session.exec(
            select(Vote).where(Vote.poll_id == poll.id, Vote.guest_id == voter_guest_id)
        ).first()
        voted_option_id = vote.option_id if vote else None

    return PollDetail(
        id=poll.id,
        question=poll.question,
        created_by=creator.username if creator else "silinmiş kullanıcı",
        total_votes=total_votes,
        created_at=poll.created_at,
        options=option_reads,
        voted_option_id=voted_option_id,
    )


@router.get("", response_model=list[PollListItem])
def list_polls(session: Session = Depends(get_session)):
    rows = session.exec(
        select(Poll, User.username, func.count(Vote.id))
        .join(User, Poll.created_by_id == User.id)
        .outerjoin(Vote, Vote.poll_id == Poll.id)
        .group_by(Poll.id, User.username)
        .order_by(Poll.created_at.desc())
    ).all()

    return [
        PollListItem(
            id=poll.id,
            question=poll.question,
            created_by=username,
            total_votes=total_votes,
            created_at=poll.created_at,
        )
        for poll, username, total_votes in rows
    ]


@router.post("", response_model=PollDetail, status_code=status.HTTP_201_CREATED)
def create_poll(
    body: PollCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    poll = Poll(question=body.question, created_by_id=user.id)
    session.add(poll)
    session.flush()  # poll.id'yi commit etmeden almak için

    for order, text in enumerate(body.options):
        session.add(PollOption(poll_id=poll.id, text=text, order=order))

    session.commit()
    session.refresh(poll)

    return _serialize_poll(session, poll, voter_user_id=user.id, voter_guest_id=None)


@router.get("/{poll_id}", response_model=PollDetail)
def get_poll(
    poll_id: int,
    session: Session = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
    guest_id: str | None = Cookie(default=None, alias=GUEST_ID_COOKIE_NAME),
):
    poll = _get_poll_or_404(session, poll_id)

    voter_guest_id = None
    if guest_id is not None:
        try:
            voter_guest_id = UUID(guest_id)
        except ValueError:
            voter_guest_id = None

    return _serialize_poll(
        session,
        poll,
        voter_user_id=user.id if user else None,
        voter_guest_id=voter_guest_id,
    )


@router.post("/{poll_id}/vote", response_model=PollDetail)
def vote(
    poll_id: int,
    body: VoteRequest,
    response: Response,
    session: Session = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
    guest_id: str | None = Cookie(default=None, alias=GUEST_ID_COOKIE_NAME),
):
    poll = _get_poll_or_404(session, poll_id)

    option = session.get(PollOption, body.option_id)
    if option is None or option.poll_id != poll.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Geçersiz seçenek")

    voter_guest_id: UUID | None = None

    if user is not None:
        existing = session.exec(
            select(Vote).where(Vote.poll_id == poll.id, Vote.user_id == user.id)
        ).first()
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bu ankette zaten oy kullandınız")

        # Ayrıca bu tarayıcıda daha önce misafir olarak oy kullanılmış mı diye bak.
        # Aksi halde: misafirken oy kullan -> hesap aç/giriş yap -> aynı ankette tekrar
        # oy kullan akışıyla "bir kişi bir ankette 1 oy" garantisi aynı tarayıcı
        # içinde bile trivially atlatılabiliyordu.
        if guest_id is not None:
            try:
                prior_guest_id = UUID(guest_id)
            except ValueError:
                prior_guest_id = None
            if prior_guest_id is not None:
                existing_guest_vote = session.exec(
                    select(Vote).where(Vote.poll_id == poll.id, Vote.guest_id == prior_guest_id)
                ).first()
                if existing_guest_vote is not None:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT, detail="Bu ankette zaten oy kullandınız"
                    )

        new_vote = Vote(poll_id=poll.id, option_id=option.id, user_id=user.id)
    else:
        if guest_id is not None:
            try:
                voter_guest_id = UUID(guest_id)
            except ValueError:
                voter_guest_id = None
        if voter_guest_id is None:
            voter_guest_id = uuid4()
        else:
            existing = session.exec(
                select(Vote).where(Vote.poll_id == poll.id, Vote.guest_id == voter_guest_id)
            ).first()
            if existing is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bu ankette zaten oy kullandınız")
        new_vote = Vote(poll_id=poll.id, option_id=option.id, guest_id=voter_guest_id)

    session.add(new_vote)
    try:
        session.commit()
    except IntegrityError:
        # Partial unique index'e (bkz. migration) yarış durumunda (aynı anda çift istek) düşen son güvence.
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bu ankette zaten oy kullandınız")

    if user is None:
        response.set_cookie(
            key=GUEST_ID_COOKIE_NAME,
            value=str(voter_guest_id),
            max_age=GUEST_ID_MAX_AGE_SECONDS,
            httponly=True,
            secure=settings.is_production,
            samesite="lax",
            path="/",
        )

    return _serialize_poll(
        session,
        poll,
        voter_user_id=user.id if user else None,
        voter_guest_id=voter_guest_id if user is None else None,
    )
