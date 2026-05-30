const CARD_API_URL = "http://127.0.0.1:8000";
const LOBBY_API_URL = "http://127.0.0.1:8003";

const gameIdValue = document.querySelector("#gameIdValue");
const createCardButton = document.querySelector("#createCardButton");
const openCardForm = document.querySelector("#openCardForm");
const openGameIdInput = document.querySelector("#openGameIdInput");
const previewCardButton = document.querySelector("#previewCardButton");
const markForm = document.querySelector("#markForm");
const markNumberInput = document.querySelector("#markNumberInput");
const gameMessage = document.querySelector("#gameMessage");
const bingoCard = document.querySelector("#bingoCard");
const cardOwner = document.querySelector("#cardOwner");
const markedCounter = document.querySelector("#markedCounter");

let currentCard = null;
let currentGameId = resolveGameId();

function getToken() {
  return localStorage.getItem("bingo_access_token");
}

function getUser() {
  return JSON.parse(localStorage.getItem("bingo_user") || "null");
}

function setGameMessage(text, type = "is-success") {
  gameMessage.classList.remove("is-error", "is-success");
  gameMessage.textContent = text;
  gameMessage.classList.add(type);
}

function isNumericId(value) {
  return /^[1-9]\d*$/.test(String(value).trim());
}

function resolveGameId() {
  const params = new URLSearchParams(window.location.search);
  const urlGameId = params.get("game_id");
  const storedGameId = localStorage.getItem("bingo_game_id");
  const gameId = String(urlGameId || storedGameId || "").trim();

  return isNumericId(gameId) ? gameId : "";
}

function renderGameId() {
  gameIdValue.textContent = currentGameId || "Не выбрана";
  openGameIdInput.value = currentGameId;
}

function syncGameId(gameId) {
  const nextGameId = String(gameId || "").trim();

  if (!isNumericId(nextGameId)) {
    return;
  }

  currentGameId = nextGameId;
  localStorage.setItem("bingo_game_id", currentGameId);

  const url = new URL(window.location.href);
  url.searchParams.set("game_id", currentGameId);
  window.history.replaceState(null, "", url);

  renderGameId();
}

function getGameId() {
  if (!currentGameId) {
    throw new Error("Сначала создай карточку или введи Game ID.");
  }

  return currentGameId;
}

function getAuthHeaders() {
  const token = getToken();

  if (!token) {
    throw new Error("Для сохранения и открытия карточки нужен вход в аккаунт. Без входа доступен только предпросмотр.");
  }

  return { Authorization: `Bearer ${token}` };
}

async function readResponse(response) {
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || "Сервис вернул ошибку.");
  }

  return data;
}

async function createRoom() {
  const response = await fetch(`${LOBBY_API_URL}/rooms`, {
    method: "POST",
    headers: getAuthHeaders(),
  });

  return readResponse(response);
}

async function createCard() {
  const gameId = getGameId();
  const response = await fetch(`${CARD_API_URL}/games/${encodeURIComponent(gameId)}/cards/me`, {
    method: "POST",
    headers: getAuthHeaders(),
  });

  return readResponse(response);
}

async function loadCard() {
  const gameId = getGameId();
  const response = await fetch(`${CARD_API_URL}/games/${encodeURIComponent(gameId)}/cards/me`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  return readResponse(response);
}

async function previewCard() {
  const user = getUser();
  const response = await fetch(`${CARD_API_URL}/cards/preview`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      game_id: currentGameId || "preview",
      user_id: user?.id ? String(user.id) : "preview-player",
    }),
  });

  return readResponse(response);
}

async function markNumber(number) {
  const gameId = getGameId();
  const response = await fetch(`${CARD_API_URL}/games/${encodeURIComponent(gameId)}/cards/me/marks`, {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ number }),
  });

  return readResponse(response);
}

function renderCard(card) {
  currentCard = card;
  syncGameId(card.game_id);
  bingoCard.querySelectorAll(".bingo-cell").forEach((cell) => cell.remove());

  card.cells.flat().forEach((cell) => {
    const button = document.createElement("button");
    button.className = "bingo-cell";
    button.type = "button";
    button.dataset.number = cell.number || "";
    button.setAttribute("aria-label", cell.is_free ? "FREE" : `${cell.letter} ${cell.number}`);

    if (cell.marked) {
      button.classList.add("is-marked");
    }

    if (cell.is_free) {
      button.classList.add("is-free");
    }

    button.innerHTML = `
      <span class="bingo-cell-letter">${cell.letter}</span>
      <strong>${cell.label}</strong>
    `;

    bingoCard.appendChild(button);
  });

  const marked = card.cells.flat().filter((cell) => cell.marked).length;
  cardOwner.textContent = `Игрок ${card.user_id}`;
  markedCounter.textContent = `${marked} отмечено`;
}

createCardButton.addEventListener("click", async () => {
  try {
    setGameMessage("Создаём комнату...");
    const room = await createRoom();

    syncGameId(room.id);
    setGameMessage("Создаём карточку...");
    renderCard(await createCard());
    setGameMessage(`Карточка создана. Game ID: ${currentGameId}.`);
  } catch (error) {
    setGameMessage(error.message, "is-error");
  }
});

openCardForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const gameId = openGameIdInput.value.trim();
  if (!isNumericId(gameId)) {
    setGameMessage("Введи числовой Game ID, например 1.", "is-error");
    return;
  }

  try {
    syncGameId(gameId);
    setGameMessage("Открываем карточку...");
    renderCard(await loadCard());
    setGameMessage(`Карточка для Game ID ${currentGameId} открыта.`);
  } catch (error) {
    setGameMessage(error.message, "is-error");
  }
});

previewCardButton.addEventListener("click", async () => {
  try {
    setGameMessage("Генерируем предпросмотр...");
    renderCard(await previewCard());
    setGameMessage("Предпросмотр карточки готов.");
  } catch (error) {
    setGameMessage(error.message, "is-error");
  }
});

markForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const number = Number(markNumberInput.value);
  if (!Number.isInteger(number) || number < 1 || number > 75) {
    setGameMessage("Введи число от 1 до 75.", "is-error");
    return;
  }

  try {
    const result = await markNumber(number);
    renderCard(result.card);
    setGameMessage(result.matched ? "Номер отмечен." : "Такого номера нет в карточке.");
  } catch (error) {
    setGameMessage(error.message, "is-error");
  }
});

renderGameId();
setGameMessage("Создай карточку или открой её по Game ID.");
