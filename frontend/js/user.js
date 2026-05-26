const USER_API_URL = "http://127.0.0.1:8002";
const LOGIN_PAGE_URL = "./login.html";

const profileStatus = document.querySelector("#profileStatus");
const profileUsername = document.querySelector("#profileUsername");
const profileEmail = document.querySelector("#profileEmail");
const profileBalance = document.querySelector("#profileBalance");
const profileAuthId = document.querySelector("#profileAuthId");
const logoutButton = document.querySelector("#logoutButton");

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

    profileUsername.textContent = data.username;
    profileEmail.textContent = data.email;
    profileBalance.textContent = `${data.balance}`;
    profileAuthId.textContent = data.auth_user_id;
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
