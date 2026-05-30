const LOGIN_PAGE_URL = "./login.html";

const homeStatus = document.querySelector("#homeStatus");

function readCachedUser() {
  try {
    return JSON.parse(localStorage.getItem("bingo_user") || "null");
  } catch {
    return null;
  }
}

function renderHomeUser(user) {
  if (!homeStatus || !user?.username) {
    return;
  }

  homeStatus.textContent = `${user.username}, выберите комнату и переходите к карточке.`;
}

async function loadHomeUser() {
  const token = localStorage.getItem("bingo_access_token");

  if (!token) {
    window.location.href = LOGIN_PAGE_URL;
    return;
  }

  renderHomeUser(readCachedUser());

  try {
    const response = await fetch("/users/me", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.detail || "Не удалось загрузить профиль.");
    }

    localStorage.setItem("bingo_user", JSON.stringify(data));
    renderHomeUser(data);
  } catch (error) {
    const cachedUser = readCachedUser();
    if (!cachedUser?.username && homeStatus) {
      homeStatus.textContent = error.message;
      homeStatus.classList.add("is-error");
    }
  }
}

loadHomeUser();
