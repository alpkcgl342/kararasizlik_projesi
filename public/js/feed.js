// index.html — tüm anketlerin akışı (en yeni en üstte).

async function renderFeed() {
  const feed = document.getElementById("feed");
  try {
    const polls = await window.api.get("/polls");

    if (polls.length === 0) {
      feed.innerHTML = `
        <div class="empty-state">
          🎲 Henüz hiç anket yok. İlk anketi sen oluştur!
        </div>
      `;
      return;
    }

    feed.innerHTML = polls
      .map(
        (poll) => `
        <a class="card poll-card" href="poll.html?id=${poll.id}">
          <strong>${escapeHtml(poll.question)}</strong>
          <div class="poll-meta">
            ${escapeHtml(poll.created_by)} · ${poll.total_votes} oy · ${timeAgo(poll.created_at)}
          </div>
        </a>
      `
      )
      .join("");
  } catch (err) {
    feed.innerHTML = `<div class="error">Anketler yüklenemedi: ${escapeHtml(err.message)}</div>`;
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

document.addEventListener("DOMContentLoaded", renderFeed);
