const AUTH_API_URL = "";
const HOME_PAGE_URL = "./home.html";

const registerForm = document.querySelector("#registerForm");
const registerMessage = document.querySelector("#registerMessage");
const loginForm = document.querySelector("#loginForm");
const loginMessage = document.querySelector("#loginMessage");

function setFormMessage(element, text, type = "is-success") {
  if (!element) {
    return;
  }

  element.classList.remove("is-error", "is-success");
  element.textContent = text;
  element.classList.add(type);
}

function saveAuthSession(authResponse) {
  localStorage.setItem("bingo_access_token", authResponse.token.access_token);
  localStorage.setItem("bingo_user", JSON.stringify(authResponse.user));
}

async function readResponse(response) {
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || "Сервис авторизации вернул ошибку.");
  }

  return data;
}

async function sendAuthRequest(path, payload) {
  const response = await fetch(`${AUTH_API_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return readResponse(response);
}

function redirectHome() {
  window.location.href = HOME_PAGE_URL;
}

function setSubmitting(form, isSubmitting) {
  form.querySelectorAll("button, input").forEach((element) => {
    element.disabled = isSubmitting;
  });
}

if (registerForm && registerMessage) {
  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(registerForm);
    const username = String(formData.get("username") || "").trim();
    const email = String(formData.get("email") || "").trim();
    const password = String(formData.get("password") || "");

    if (!username || !email || password.length < 6) {
      setFormMessage(registerMessage, "Заполните все поля. Пароль должен быть не короче 6 символов.", "is-error");
      return;
    }

    setSubmitting(registerForm, true);
    try {
      setFormMessage(registerMessage, "Создаем аккаунт...");
      const authResponse = await sendAuthRequest("/auth/register", { username, email, password });
      saveAuthSession(authResponse);
      setFormMessage(registerMessage, "Аккаунт создан. Открываем главную...");
      setTimeout(redirectHome, 350);
    } catch (error) {
      setFormMessage(registerMessage, error.message, "is-error");
      setSubmitting(registerForm, false);
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
      setFormMessage(loginMessage, "Введите email и пароль не короче 6 символов.", "is-error");
      return;
    }

    setSubmitting(loginForm, true);
    try {
      setFormMessage(loginMessage, "Проверяем доступ...");
      const authResponse = await sendAuthRequest("/auth/login", { email, password });
      saveAuthSession(authResponse);
      setFormMessage(loginMessage, "Вход выполнен. Открываем главную...");
      setTimeout(redirectHome, 350);
    } catch (error) {
      setFormMessage(loginMessage, error.message, "is-error");
      setSubmitting(loginForm, false);
    }
  });
}
