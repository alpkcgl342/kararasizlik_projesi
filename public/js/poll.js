// poll.html?id=<id> — anket detay + oylama.

function getPollId() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get("id");
  return id ? Number(id) : null;
}

function renderOptions(poll) {
  const hasVoted = poll.voted_option_id !== null && poll.voted_option_id !== undefined;

  return poll.options
    .map((opt) => {
      const isChosen = opt.id === poll.voted_option_id;
      const classes = ["option"];
      if (hasVoted) classes.push("voted");
      if (isChosen) classes.push("chosen");

      return `
        <div class="${classes.join(" ")}" data-option-id="${opt.id}" data-clickable="${!hasVoted}">
          <div class="option-bar" data-target-width="${hasVoted ? opt.percentage : 0}"></div>
          <div class="option-content">
            <span>${isChosen ? "✓ " : ""}${escapeHtml(opt.text)}</span>
            ${hasVoted ? `<span>${opt.percentage}% (${opt.votes})</span>` : ""}
          </div>
        </div>
      `;
    })
    .join("");
}

function renderPoll(poll) {
  const container = document.getElementById("poll-detail");
  const hasVoted = poll.voted_option_id !== null && poll.voted_option_id !== undefined;

  container.innerHTML = `
    <div class="card">
      <h1>${escapeHtml(poll.question)}</h1>
      <div class="poll-meta">
        ${escapeHtml(poll.created_by)} · ${poll.total_votes} oy · ${timeAgo(poll.created_at)}
      </div>
      <div id="options" style="margin-top: 1rem;">
        ${renderOptions(poll)}
      </div>
      ${hasVoted ? "" : '<p class="muted">Bir seçeneğe tıklayarak oy kullanabilirsin.</p>'}
      <div id="vote-error" class="error" style="display:none"></div>
    </div>
  `;

  if (!hasVoted) {
    container.querySelectorAll(".option").forEach((el) => {
      el.addEventListener("click", () => castVote(poll.id, Number(el.dataset.optionId)));
    });
  }

  animateBars(container);
}

// Sonuç barlarını 0'dan hedef yüzdeye "dolarak" animasyonla göster.
function animateBars(container) {
  const bars = container.querySelectorAll(".option-bar");
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      bars.forEach((bar) => {
        bar.style.width = `${bar.dataset.targetWidth}%`;
      });
    });
  });
}

let voteInFlight = false;

async function castVote(pollId, optionId) {
  if (voteInFlight) return;
  voteInFlight = true;

  const errorBox = document.getElementById("vote-error");
  errorBox.style.display = "none";
  try {
    const updated = await window.api.post(`/polls/${pollId}/vote`, { option_id: optionId });
    renderPoll(updated);
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.style.display = "block";
  } finally {
    voteInFlight = false;
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

async function loadPoll() {
  const container = document.getElementById("poll-detail");
  const pollId = getPollId();

  if (!pollId) {
    container.innerHTML = `<div class="error">Geçersiz anket bağlantısı.</div>`;
    return;
  }

  try {
    const poll = await window.api.get(`/polls/${pollId}`);
    renderPoll(poll);
  } catch (err) {
    container.innerHTML = `<div class="error">Anket yüklenemedi: ${escapeHtml(err.message)}</div>`;
  }
}

document.addEventListener("DOMContentLoaded", loadPoll);
