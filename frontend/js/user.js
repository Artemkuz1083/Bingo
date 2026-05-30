const USER_API_URL = "";
const LOGIN_PAGE_URL = "./login.html";

const profileStatus = document.querySelector("#profileStatus");
const profileUsername = document.querySelector("#profileUsername");
const profileEmail = document.querySelector("#profileEmail");
const profileBalance = document.querySelector("#profileBalance");
const profileAuthId = document.querySelector("#profileAuthId");
const logoutButton = document.querySelector("#logoutButton");

function readCachedUser() {
  try {
    return JSON.parse(localStorage.getItem("bingo_user") || "null");
  } catch {
    return null;
  }
}

function renderProfile(data) {
  if (!data) {
    return;
  }

  profileUsername.textContent = data.username || "Нет данных";
  profileEmail.textContent = data.email || "Нет данных";
  profileBalance.textContent = `${data.balance ?? "0.00"}`;
  profileAuthId.textContent = data.auth_user_id ?? data.id ?? "Нет данных";
}

function setProfileStatus(text, type = "is-success") {
  if (!profileStatus) {
    return;
  }

  profileStatus.classList.remove("is-error", "is-success");
  profileStatus.textContent = text;
  profileStatus.classList.add(type);
}

function clearSessionAndRedirect() {
  localStorage.removeItem("bingo_access_token");
  localStorage.removeItem("bingo_user");
  window.location.href = LOGIN_PAGE_URL;
}

async function loadProfile() {
  const token = localStorage.getItem("bingo_access_token");

  if (!token) {
    clearSessionAndRedirect();
    return;
  }

  renderProfile(readCachedUser());

  try {
    const response = await fetch(`${USER_API_URL}/users/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.detail || "Не удалось загрузить профиль.");
    }

    renderProfile(data);
    localStorage.setItem("bingo_user", JSON.stringify(data));
    setProfileStatus("Сигнал профиля принят. Канал стабилен.");
  } catch (error) {
    setProfileStatus(error.message, "is-error");
  }
}

if (logoutButton) {
  logoutButton.addEventListener("click", clearSessionAndRedirect);
}

loadProfile();
