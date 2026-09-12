# Kararsızım — Proje Planı ve Teknik Spesifikasyon

> Bu doküman, "Kararsızım" web uygulamasının Claude Code ile geliştirilmesi için hazırlanmış kapsamlı bir referans dosyasıdır. Claude Code'a bu dosyayı vererek projeyi adım adım (fazlar halinde) inşa ettirebilirsin. Tüm bölümü tek seferde uygulatmak zorunda değilsin — "Yol Haritası" bölümündeki fazları sırayla Claude Code'a verebilirsin.

---

## 1. Proje Özeti

**Proje adı:** Kararsızım

**Amaç:** Kullanıcıların kararsız kaldıkları günlük konularda (ör. "Bugün sinemaya mı gitsem yoksa restorana mı?") hızlıca bir anket oluşturup platformdaki diğer kullanıcılara danışabildiği, herkesin oy kullanarak fikir belirtebildiği bir anket/oylama platformu.

**Hedef kitle:** Genç ve genç yetişkin kullanıcılar; hızlı, eğlenceli, sosyal medya hissiyatına yakın bir deneyim bekleniyor.

**Bu aşamadaki hedef:** Karmaşık olmayan, çalışan bir **prototip** ortaya çıkarmak. Mimari basit tutulacak, ileride kademeli olarak geliştirilecek.

---

## 2. Kullanıcı Rolleri

| Rol | Anketleri görüntüleme | Oy kullanma | Anket oluşturma |
|---|---|---|---|
| **Misafir** (üye değil) | ✅ | ✅ | ❌ (üye olması gerekir) |
| **Üye** | ✅ | ✅ | ✅ |

- Platformda **takip sistemi yok**: kullanıcılar birbirini takip edemez, kimseye özel içerik yoktur.
- Her kullanıcı (üye veya misafir) platformdaki **tüm anketleri** görebilir ve oy kullanabilir.
- Anket oluşturmak isteyen misafir kullanıcı, kayıt ol / giriş yap akışına yönlendirilir.

---

## 3. Kullanıcı Yönetimi

Kayıt formunda istenen alanlar:

- **E-posta** (benzersiz, giriş için kullanılır, herkese açık gösterilmez)
- **Parola**
- **Kullanıcı adı** (benzersiz olmalı — anketlerde ve oylarda görünen isim budur)

Kurallar:

- Anketlerde ve varsa oy listelerinde **sadece kullanıcı adı** gösterilir, e-posta hiçbir yerde görünmez.
- Parolalar **passlib (bcrypt)** ile hash'lenerek saklanır, düz metin parola asla veritabanına yazılmaz.
- Oturum yönetimi **JWT (JSON Web Token)** ile yapılır: kullanıcı giriş yaptığında sunucu bir JWT üretir ve bunu **httpOnly cookie** içinde tarayıcıya yazar. Bu sayede serverless fonksiyonlar arasında sunucu taraflı bir session deposu (Redis vb.) tutmaya gerek kalmaz — her istek, cookie'deki token doğrulanarak kimliklendirilir.
- v1 kapsamında e-posta doğrulama (aktivasyon maili) **yok** — sadece kayıt ol / giriş yap. İstenirse sonraki fazda eklenebilir.

---

## 4. Temel Özellikler (v1 Kapsamı)

### 4.1 Anket Oluşturma (sadece üyeler)
- Bir soru metni (ör. "Bugün sinemaya mı gitsem restorana mı?")
- En az **2**, en fazla **5** seçenek (dinamik olarak "+ Seçenek ekle" butonuyla eklenir)
- Oluşturan kullanıcının adı ankette görünür
- Anketler **süresiz açık** kalır, otomatik kapanma yok (v1 kapsamında)

### 4.2 Anket Listeleme (Ana Akış)
- Ana sayfa, tüm anketleri **en yeni en üstte** olacak şekilde basit bir akış (feed) halinde listeler.
- v1'de kategori, etiket veya arama **yok** — sade ve hızlı bir liste yeterli.
- Her kart üzerinde: soru metni, oluşturan kullanıcı adı, toplam oy sayısı, oluşturulma zamanı (ör. "3 saat önce") gösterilir.

### 4.3 Oylama
- Kullanıcı (üye veya misafir) bir anketin seçeneklerinden birine tıklayarak oy kullanır.
- Oy kullanıldıktan sonra sonuçlar **yüzdelik bar** şeklinde anlık gösterilir (sayfa yenilenmeden, `fetch()` ile).
- **Bir kullanıcı bir ankette yalnızca 1 kez oy kullanabilir:**
  - **Üyeler için:** `votes` tablosunda `(user_id, poll_id)` ikilisi **unique constraint** ile kısıtlanır — veritabanı seviyesinde garanti edilir. Kimlik, giriş cookie'sindeki JWT'den okunur.
  - **Misafirler için:** Kullanıcı takibi/hesabı olmadığından, tarayıcıya özel rastgele bir `guest_id` üretilip **cookie**'de saklanır (JWT gerekmez, sadece rastgele bir UUID); oy bu `guest_id` ile ilişkilendirilir ve `(guest_id, poll_id)` ikilisi kontrol edilir. Bu yöntem %100 kusursuz değildir (kullanıcı çerezi silip tekrar oy kullanabilir) ama prototip için yeterlidir ve **kişisel veri/takip içermez** (sadece anonim bir oturum kimliğidir, kullanıcı profiline bağlanmaz).
- Oy kullanan kişi daha sonra tekrar o anketi ziyaret ettiğinde, oy kullanmış olduğu seçenek işaretli şekilde sonuçları görür (tekrar oy kullanamaz, sadece sonuçları izler).

### 4.4 Anket Detay Sayfası
- Anketin sorusu, tüm seçenekleri, her seçeneğin oy sayısı/yüzdesi, toplam oy sayısı ve oluşturan kullanıcı adı gösterilir.

---

## 5. Kapsam Dışı (v1'de Yapılmayacaklar)

Bu özellikler bilinçli olarak v1 dışında bırakılmıştır, ileride ayrı fazlarda değerlendirilebilir:

- Kullanıcı takip sistemi / arkadaşlık
- Anketlere yorum yapma
- Kategori, etiket veya arama/filtreleme
- Anket süresi/otomatik kapanma
- Bildirimler (push/e-posta)
- Şikayet/moderasyon sistemi
- E-posta doğrulama, şifre sıfırlama akışı
- Anket silme/düzenleme (v1'de anketler oluşturulduktan sonra sabittir; istenirse "kendi anketimi sil" basit bir özellik olarak sonraki fazda eklenebilir)
- Admin panel (Django'nun aksine FastAPI'de hazır gelmiyor; v1'de gerekli değil, istenirse `sqladmin` ile sonraki fazda eklenebilir)

---

## 6. Teknoloji Yığını

| Katman | Teknoloji |
|---|---|
| Backend | Python, **FastAPI** (async/ASGI — Vercel'in serverless Python modeliyle native uyumlu) |
| ORM / Migration | **SQLModel** (SQLAlchemy + Pydantic birleşimi) + **Alembic** |
| Veritabanı | Supabase (yönetilen Postgres) — FastAPI'ye standart Postgres bağlantı dizesi (`DATABASE_URL`) ile bağlanılır |
| Kimlik doğrulama | **JWT** (httpOnly cookie içinde) + **passlib/bcrypt** ile parola hash'leme |
| Frontend | Saf HTML, CSS, JavaScript — statik dosyalar olarak Vercel tarafından doğrudan sunulur; backend'e sadece `fetch()` ile JSON istekleri atılır (SPA framework yok) |
| Deployment | Vercel (statik frontend + `/api/*` altında FastAPI serverless fonksiyonları) |

### Neden Django yerine FastAPI? (Karar Gerekçesi)

- **Vercel uyumu:** Vercel'in Python desteği temelde "bir ASGI/WSGI callable'ı serverless fonksiyon olarak çalıştırma" mantığına dayanır. FastAPI bu modele native (ASGI) uyduğu için resmi örnek şablonlarda da yer alır; Django (WSGI) serverless'e daha "zorlama" bir şekilde oturur ve statik/admin dosya servisi ekstra yapılandırma ister.
- **Hafiflik:** FastAPI + SQLModel, Django'ya kıyasla çok daha az bağımlılığa sahiptir → daha küçük paket boyutu, daha hızlı soğuk başlangıç (cold start) — serverless'te bu doğrudan kullanıcı deneyimine yansır.
- **Mimari sadeliği:** Statik frontend + ince bir JSON API mimarisi, Vercel'in en güçlü olduğu alana (statik hosting + hafif fonksiyonlar) tam oturur.
- **Bedeli:** Django'nun hazır gelen auth sistemi, ORM+migration ve admin panelinden vazgeçiyoruz; bunların yerine yukarıdaki hafif kütüphaneleri elle bağlıyoruz. Bu, prototip için makul bir ek karmaşıklık — toplam kod hacmi Django'dakinden büyük farklı olmayacak.

### ⚠️ Supabase bağlantısı hakkında not

- Supabase burada sadece **yönetilen bir Postgres veritabanı** olarak kullanılacak; Supabase'in Auth/Storage/Realtime servisleri kullanılmıyor.
- Serverless fonksiyonlar her istekte yeni bir bağlantı açabileceğinden, veritabanını yormamak için Supabase'in sunduğu **connection pooling modu (PgBouncer, `?pgbouncer=true`)** kullanılmalı ve SQLAlchemy tarafında `NullPool` (veya benzeri, bağlantıyı istek sonunda bırakan bir pool ayarı) tercih edilmelidir.

---

## 7. Veri Modeli (SQLModel — taslak)

```python
# models.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=32)
    email: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    polls: list["Poll"] = Relationship(back_populates="created_by")


class Poll(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question: str = Field(max_length=280)
    created_by_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    created_by: Optional[User] = Relationship(back_populates="polls")
    options: list["PollOption"] = Relationship(back_populates="poll")


class PollOption(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    poll_id: int = Field(foreign_key="poll.id")
    text: str = Field(max_length=120)
    order: int = Field(default=0)

    poll: Optional[Poll] = Relationship(back_populates="options")


class Vote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    poll_id: int = Field(foreign_key="poll.id")
    option_id: int = Field(foreign_key="polloption.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    guest_id: Optional[UUID] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Not: (poll_id, user_id) ve (poll_id, guest_id) için "partial unique index"
    # Alembic migration'ında elle eklenmeli (SQLModel/SQLAlchemy Core seviyesinde,
    # PostgreSQL'in "WHERE user_id IS NOT NULL" koşullu unique index özelliğiyle):
    #
    #   CREATE UNIQUE INDEX unique_vote_per_user_per_poll
    #     ON vote (poll_id, user_id) WHERE user_id IS NOT NULL;
    #   CREATE UNIQUE INDEX unique_vote_per_guest_per_poll
    #     ON vote (poll_id, guest_id) WHERE guest_id IS NOT NULL;
```

> Not: 2–5 seçenek sınırı hem frontend'de (form validasyonu) hem de backend'de (Pydantic/FastAPI request body validasyonu, ör. `options: list[str] = Field(min_length=2, max_length=5)`) doğrulanmalıdır.

---

## 8. Sayfa Listesi (Statik Frontend)

Tüm sayfalar düz HTML dosyaları olarak sunulur, veriler `fetch()` ile `/api/*` endpoint'lerinden çekilir:

1. **Ana Sayfa (Akış)** `/index.html` — tüm anketlerin listesi, en yeni en üstte
2. **Anket Detay** `/poll.html?id=<id>` — soru, seçenekler, oylama arayüzü, sonuçlar
3. **Anket Oluştur** `/new-poll.html` — sadece giriş yapmış kullanıcılar erişebilir (JS ile cookie/JWT kontrolü, yoksa giriş sayfasına yönlendirme)
4. **Kayıt Ol** `/register.html`
5. **Giriş Yap** `/login.html`
6. *(opsiyonel, sonraki faz)* **Profilim** `/profile.html` — kullanıcının oluşturduğu anketler

## 9. API Endpoint Taslağı (FastAPI, `/api/*`)

| Metod | Endpoint | Açıklama |
|---|---|---|
| GET | `/api/polls` | Tüm anketleri listele (en yeni en üstte) |
| GET | `/api/polls/{id}` | Anket detayı + seçenekler + oy sayıları |
| POST | `/api/polls` | Yeni anket oluştur (JWT cookie gerekli) |
| POST | `/api/polls/{id}/vote` | Oy kullan — body: `{ "option_id": ... }`; misafirse `guest_id` cookie'sini okur/oluşturur |
| POST | `/api/auth/register` | Kayıt ol — body: `{ username, email, password }` |
| POST | `/api/auth/login` | Giriş yap — başarılıysa JWT'yi httpOnly cookie olarak set eder |
| POST | `/api/auth/logout` | Çıkış — cookie'yi temizler |
| GET | `/api/auth/me` | Giriş yapmış kullanıcının bilgisini döner (frontend'in "giriş yapılı mı" kontrolü için) |

---

## 10. Arayüz (UI/UX) Yönergeleri

- **Genel his:** Genç kitleye hitap eden, canlı, enerjik ama dağınık olmayan bir tasarım.
- **Arka plan:** Açık (beyaz veya çok açık gri/pastel) arka plan.
- **Renkler:** Canlı/parlak vurgu renkleri (ör. mor, turuncu, pembe, turkuaz gibi bir "gradient" veya canlı vurgu paleti) — ama arka plan sade kaldığı için renkler **üstüne binen ton olarak** (kartlar, butonlar, oy barları, başlıklar üzerinde) kullanılmalı. Genel yüzey temiz kalmalı, aşırı renk kirliliğinden kaçınılmalı.
- **Tipografi:** Modern, yuvarlak hatlı bir sistem fontu (ör. Poppins, Inter, Nunito gibi Google Fonts) — büyük ve okunaklı başlıklar.
- **Bileşenler:**
  - Anket kartları: yuvarlatılmış köşeler, hafif gölge, hover'da hafif büyüme/vurgu animasyonu
  - Oylama sonuç barları: her seçenek için canlı renkte dolan bir ilerleme çubuğu + yüzde
  - Butonlar: belirgin, canlı renkli, yuvarlak köşeli, tıklanabilirliği net
- **Duyarlılık (responsive):** Mobil öncelikli tasarım — hedef kitlenin büyük kısmı telefondan kullanacaktır.
- Sayfa geçişlerinde ve oylama anında küçük **micro-interaction** animasyonları (ör. buton tıklamasında hafif "pop" efekti, sonuç barının dolma animasyonu) genç/dinamik his katar.

---

## 11. Proje Klasör Yapısı (Önerilen)

```
kararsizim/
├── vercel.json
├── requirements.txt
├── .env.example
├── alembic.ini
├── alembic/                 # migration dosyaları
├── api/                     # FastAPI backend (Vercel /api/* olarak servis eder)
│   ├── main.py               # FastAPI app + router include
│   ├── models.py             # SQLModel tabloları (Bölüm 7)
│   ├── database.py           # engine/session kurulumu
│   ├── auth.py                # JWT üretim/doğrulama, parola hash
│   ├── deps.py                 # ortak dependency'ler (get_current_user vb.)
│   └── routers/
│       ├── auth.py            # /api/auth/*
│       └── polls.py           # /api/polls/*
└── public/                  # statik frontend (Vercel doğrudan sunar)
    ├── index.html
    ├── poll.html
    ├── new-poll.html
    ├── register.html
    ├── login.html
    ├── css/
    │   └── style.css
    └── js/
        ├── api.js             # fetch() yardımcı fonksiyonları
        ├── feed.js
        ├── poll.js
        └── auth.js
```

---

## 12. Ortam Değişkenleri (.env)

```
DATABASE_URL=postgresql://<supabase-connection-string-with-pgbouncer>
JWT_SECRET=
JWT_EXPIRE_MINUTES=10080
ENVIRONMENT=production
```

---

## 13. Varsayımlar (Bu Doküman Hazırlanırken Verilen Kararlar)

- Her ankette kullanıcı başına (üye: hesap üzerinden JWT ile, misafir: tarayıcı `guest_id`'si üzerinden) **1 oy** hakkı vardır.
- Anketlerin **bitiş süresi yoktur**, süresiz açık kalır.
- Ana sayfa **basit bir akış (feed)** şeklindedir; kategori veya arama v1'de yoktur.
- Backend olarak Django yerine **FastAPI** seçildi (Bölüm 6'daki gerekçeyle), frontend statik dosyalar + JSON API mimarisine göre kurgulandı.
- Bu varsayımlar ileride kolayca değiştirilebilir/genişletilebilir; sabit kurallar değildir.

---

## 14. Yol Haritası (Fazlar)

Bu fazları Claude Code'a ayrı ayrı, sırayla verebilirsin:

**Faz 1 — Temel İskelet**
- FastAPI projesinin kurulması (`api/` klasörü), SQLModel modellerinin (`User`, `Poll`, `PollOption`, `Vote`) yazılması
- Alembic kurulumu ve ilk migration'ın oluşturulması
- Kayıt ol / giriş yap / çıkış yap endpoint'lerinin (JWT + bcrypt ile) çalışır hale getirilmesi

**Faz 2 — Anket Oluşturma & Oylama**
- Anket oluşturma endpoint'i (2–5 seçenek validasyonu) ve `/new-poll.html` formu
- `/api/polls` listeleme endpoint'i ve `/index.html` akışı
- Oylama endpoint'i, üye/misafir oy sınırlaması, sonuçların yüzdelik bar ile gösterimi

**Faz 3 — Arayüz (UI/UX)**
- Bölüm 10'daki tasarım yönergelerine göre CSS/JS ile arayüzün canlı, genç kitleye hitap eden hale getirilmesi
- Responsive/mobil uyum

**Faz 4 — Veritabanı & Deployment**
- Supabase Postgres veritabanı kurulumu ve bağlantısı (pgbouncer modu ile)
- Vercel deployment yapılandırması (`vercel.json` — `/api` için Python runtime, `/public` için statik hosting)
- Ortam değişkenlerinin Vercel'de tanımlanması, canlıya alma

**Faz 5 — İyileştirmeler (opsiyonel, sonraki adım)**
- Kendi anketini silme
- Basit kategori/etiketleme
- Anket süresi/otomatik kapanma
- E-posta doğrulama, şifre sıfırlama
- Admin panel (`sqladmin`)

---

## 15. Claude Code'a Verirken Kullanılabilecek Örnek Komut

> "Bu dokümandaki Faz 1'i uygula: FastAPI projesini kur, SQLModel modellerini yaz, Alembic migration'ını oluştur, auth (kayıt/giriş/çıkış) endpoint'lerini JWT ile çalışır hale getir. Diğer fazlara henüz geçme."

Bu şekilde her fazı ayrı ayrı, önceki fazın çıktısını gözden geçirdikten sonra ilerletebilirsin.
