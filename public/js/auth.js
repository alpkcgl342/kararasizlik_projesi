// Ortak auth yardımcıları: giriş durumunu kontrol etme, nav bar'ı doldurma.

async function getCurrentUser() {
  const data = await window.api.get("/auth/me");
  return data.user; // null ya da {id, username, created_at}
}

async function requireLogin(redirectTo = "login.html") {
  const user = await getCurrentUser();
  if (!user) {
    window.location.href = redirectTo;
  }
  return user;
}

async function initNav() {
  const nav = document.getElementById("nav-auth");
  if (!nav) return;

  let user = null;
  try {
    user = await getCurrentUser();
  } catch {
    // /api/auth/me başarısız olursa çıkış yapılmış gibi davran
  }

  if (user) {
    nav.innerHTML = `
      <span class="username-badge">${user.username}</span>
      <a href="new-poll.html" class="btn">+ Anket</a>
      <button id="logout-btn" type="button">Çıkış</button>
    `;
    document.getElementById("logout-btn").addEventListener("click", async () => {
      await window.api.post("/auth/logout");
      window.location.href = "index.html";
    });
  } else {
    nav.innerHTML = `
      <a href="login.html">Giriş Yap</a>
      <a href="register.html" class="btn">Kayıt Ol</a>
    `;
  }
}

document.addEventListener("DOMContentLoaded", initNav);
