
const CARD_API_URL = "http://127.0.0.1:8000";

const gameIdInput = document.querySelector("#gameIdInput");
const createCardButton = document.querySelector("#createCardButton");
const previewCardButton = document.querySelector("#previewCardButton");
const markForm = document.querySelector("#markForm");
const markNumberInput = document.querySelector("#markNumberInput");
const gameMessage = document.querySelector("#gameMessage");
const bingoCard = document.querySelector("#bingoCard");
const cardOwner = document.querySelector("#cardOwner");
const markedCounter = document.querySelector("#markedCounter");

let currentCard = null;

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

function getGameId() {
  return gameIdInput.value.trim() || "game-1";
}

function getAuthHeaders() {
  const token = getToken();

  if (!token) {
    throw new Error("Для сохранения карточки нужен вход в аккаунт. Используй предпросмотр без токена.");
  }

  return { Authorization: `Bearer ${token}` };
}

async function readResponse(response) {
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || "Card service вернул ошибку.");
  }

  return data;
}

async function createOrLoadCard() {
  const gameId = getGameId();
  const response = await fetch(`${CARD_API_URL}/games/${encodeURIComponent(gameId)}/cards/me`, {
    method: "POST",
    headers: getAuthHeaders(),
  });

  return readResponse(response);
}

async function previewCard() {
  const gameId = getGameId();
  const user = getUser();
  const response = await fetch(`${CARD_API_URL}/cards/preview`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      game_id: gameId,
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
    setGameMessage("Загружаем карточку...");
    renderCard(await createOrLoadCard());
    setGameMessage("Карточка готова.");
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

previewCardButton.click();
