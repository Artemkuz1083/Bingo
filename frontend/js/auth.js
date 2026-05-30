const AUTH_API_URL = "";
const HOME_PAGE_URL = "./home.html";

const registerForm = document.querySelector("#registerForm");
const registerMessage = document.querySelector("#registerMessage");
const loginForm = document.querySelector("#loginForm");
const loginMessage = document.querySelector("#loginMessage");

function setFormMessage(element, text, type) {
  element.classList.remove("is-error", "is-success");
  element.textContent = text;
  element.classList.add(type);
}

function saveAuthSession(authResponse) {
  localStorage.setItem("bingo_access_token", authResponse.token.access_token);
  localStorage.setItem("bingo_user", JSON.stringify(authResponse.user));
}

async function sendAuthRequest(path, payload) {
  const response = await fetch(`${AUTH_API_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || "Сервис авторизации вернул ошибку.");
  }

  return data;
}

function redirectHome() {
  window.location.href = HOME_PAGE_URL;
}

if (registerForm && registerMessage) {
  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(registerForm);
    const username = String(formData.get("username") || "").trim();
    const email = String(formData.get("email") || "").trim();
    const password = String(formData.get("password") || "");

    if (!username || !email || password.length < 6) {
      setFormMessage(
        registerMessage,
        "Заполни все поля. Пароль минимум 6 символов.",
        "is-error",
      );
      return;
    }

    try {
      setFormMessage(registerMessage, "Создаем аккаунт...", "is-success");
      const authResponse = await sendAuthRequest("/auth/register", {
        username,
        email,
        password,
      });
      saveAuthSession(authResponse);
      setFormMessage(registerMessage, "Аккаунт создан. Перенаправляем...", "is-success");
      setTimeout(redirectHome, 450);
    } catch (error) {
      setFormMessage(registerMessage, error.message, "is-error");
    }
  });
}

if (loginForm && loginMessage) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(loginForm);
    const email = String(formData.get("email") || "").trim();
    const password = String(formData.get("password") || "");

    if (!email || password.length < 6) {
      setFormMessage(
        loginMessage,
        "Введи email и пароль минимум из 6 символов.",
        "is-error",
      );
      return;
    }

    try {
      setFormMessage(loginMessage, "Проверяем доступ...", "is-success");
      const authResponse = await sendAuthRequest("/auth/login", {
        email,
        password,
      });
      saveAuthSession(authResponse);
      setFormMessage(loginMessage, "Доступ подтвержден. Перенаправляем...", "is-success");
      setTimeout(redirectHome, 450);
    } catch (error) {
      setFormMessage(loginMessage, error.message, "is-error");
    }
  });
}
