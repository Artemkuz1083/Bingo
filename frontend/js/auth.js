const registerForm = document.querySelector("#registerForm");
const registerMessage = document.querySelector("#registerMessage");
const loginForm = document.querySelector("#loginForm");
const loginMessage = document.querySelector("#loginMessage");

function setFormMessage(element, text, type) {
  element.classList.remove("is-error", "is-success");
  element.textContent = text;
  element.classList.add(type);
}

if (registerForm && registerMessage) {
  registerForm.addEventListener("submit", (event) => {
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

    setFormMessage(
      registerMessage,
      "Запрос регистрации готов к отправке в auth-service.",
      "is-success",
    );
  });
}

if (loginForm && loginMessage) {
  loginForm.addEventListener("submit", (event) => {
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

    setFormMessage(
      loginMessage,
      "Запрос входа готов к отправке в auth-service.",
      "is-success",
    );
  });
}
