// new-poll.html — sadece giriş yapmış kullanıcılar erişebilir.

const MIN_OPTIONS = 2;
const MAX_OPTIONS = 5;

function optionRowHtml(index) {
  return `
    <div class="option-row" data-index="${index}">
      <input type="text" maxlength="120" placeholder="Seçenek ${index + 1}" required />
      <button type="button" class="remove-option" aria-label="Seçeneği sil">✕</button>
    </div>
  `;
}

function refreshOptionRows() {
  const container = document.getElementById("options");
  const rows = container.querySelectorAll(".option-row");

  rows.forEach((row, i) => {
    row.querySelector("input").placeholder = `Seçenek ${i + 1}`;
    row.querySelector(".remove-option").disabled = rows.length <= MIN_OPTIONS;
  });

  document.getElementById("add-option").disabled = rows.length >= MAX_OPTIONS;
}

function addOptionRow() {
  const container = document.getElementById("options");
  const count = container.querySelectorAll(".option-row").length;
  if (count >= MAX_OPTIONS) return;

  container.insertAdjacentHTML("beforeend", optionRowHtml(count));
  refreshOptionRows();
}

function initOptionRows() {
  const container = document.getElementById("options");
  container.innerHTML = optionRowHtml(0) + optionRowHtml(1);
  refreshOptionRows();

  container.addEventListener("click", (e) => {
    if (e.target.classList.contains("remove-option")) {
      const rows = container.querySelectorAll(".option-row");
      if (rows.length <= MIN_OPTIONS) return;
      e.target.closest(".option-row").remove();
      refreshOptionRows();
    }
  });

  document.getElementById("add-option").addEventListener("click", addOptionRow);
}

async function handleSubmit(e) {
  e.preventDefault();
  const errorBox = document.getElementById("form-error");
  errorBox.style.display = "none";

  const question = document.getElementById("question").value.trim();
  const options = Array.from(document.querySelectorAll("#options input")).map((el) => el.value.trim());

  if (options.some((o) => !o)) {
    errorBox.textContent = "Boş seçenek bırakma.";
    errorBox.style.display = "block";
    return;
  }

  try {
    const poll = await window.api.post("/polls", { question, options });
    window.location.href = `poll.html?id=${poll.id}`;
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.style.display = "block";
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  await requireLogin();
  initOptionRows();
  document.getElementById("new-poll-form").addEventListener("submit", handleSubmit);
});
