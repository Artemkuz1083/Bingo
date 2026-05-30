const CARD_API_URL = "http://127.0.0.1:8004";
const GAME_ENGINE_API_URL = "http://127.0.0.1:8005";
const WINNER_API_URL = "http://127.0.0.1:8006";

const gameIdValue = document.querySelector("#gameIdValue");
const cardActionButton = document.querySelector("#cardActionButton");
const refreshStateButton = document.querySelector("#refreshStateButton");
const markLastBallButton = document.querySelector("#markLastBallButton");
const claimBingoButton = document.querySelector("#claimBingoButton");
const gameStatusValue = document.querySelector("#gameStatusValue");
const lastBallValue = document.querySelector("#lastBallValue");
const drawnCountValue = document.querySelector("#drawnCountValue");
const gameMessage = document.querySelector("#gameMessage");
const bingoCard = document.querySelector("#bingoCard");
const cardOwner = document.querySelector("#cardOwner");
const markedCounter = document.querySelector("#markedCounter");

let currentCard = null;
let currentGameId = resolveGameId();
let lastBallNumber = null;
let busy = false;
let autoRefreshTimer = null;

function getToken() {
  return localStorage.getItem("bingo_access_token");
}

function clearAuthSession() {
  localStorage.removeItem("bingo_access_token");
  localStorage.removeItem("bingo_user");
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
  const fromUrl = params.get("game_id");
  const fromStorage = localStorage.getItem("bingo_game_id");
  const gameId = String(fromUrl || fromStorage || "").trim();
  return isNumericId(gameId) ? gameId : "";
}

function renderGameId() {
  gameIdValue.textContent = currentGameId || "Не выбрана";
}

function getGameId() {
  if (!currentGameId) {
    throw new Error("Сначала создайте комнату в лобби.");
  }
  return currentGameId;
}

function getAuthHeaders() {
  const token = getToken();
  if (!token) {
    throw new Error("Нужно войти в аккаунт.");
  }
  return { Authorization: `Bearer ${token}` };
}

async function readResponse(response) {
  const data = await response.json().catch(() => ({}));

  if (response.status === 401) {
    clearAuthSession();
    throw new Error("Сессия истекла. Войди заново.");
  }

  if (!response.ok) {
    throw new Error(data.detail || "Сервис вернул ошибку.");
  }

  return data;
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
    headers: getAuthHeaders(),
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

async function loadGameState() {
  const gameId = getGameId();
  const response = await fetch(`${GAME_ENGINE_API_URL}/game/${encodeURIComponent(gameId)}/state`);
  return readResponse(response);
}

async function submitWinnerClaim() {
  const gameId = getGameId();
  const response = await fetch(`${WINNER_API_URL}/games/${encodeURIComponent(gameId)}/winner-claims`, {
    method: "POST",
    headers: getAuthHeaders(),
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
  cardActionButton.querySelector("span").textContent = "Открыть карточку";
  claimBingoButton.disabled = false;
  markLastBallButton.disabled = !lastBallNumber;
}

function renderGameState(state) {
  lastBallNumber = state.last_ball?.number || null;
  gameStatusValue.textContent = state.is_active ? "Игра идет" : "Игра не запущена";
  lastBallValue.textContent = state.last_ball?.label || "...";
  drawnCountValue.textContent = `${state.drawn_count || 0} выпало`;
  markLastBallButton.disabled = !lastBallNumber || !currentCard;
}

async function run(action) {
  if (busy) {
    return;
  }

  busy = true;
  try {
    await action();
  } catch (error) {
    setGameMessage(error.message, "is-error");
  } finally {
    busy = false;
  }
}

cardActionButton.addEventListener("click", () => run(async () => {
  try {
    setGameMessage("Открываем карточку...");
    renderCard(await loadCard());
    setGameMessage("Карточка открыта.");
  } catch (error) {
    if (!String(error.message).includes("Card not found")) {
      throw error;
    }
    setGameMessage("Создаем карточку...");
    renderCard(await createCard());
    setGameMessage("Карточка создана.");
  }

  await refreshGameState();
}));

async function refreshGameState() {
  const state = await loadGameState();
  renderGameState(state);
  return state;
}

function startAutoRefresh() {
  if (autoRefreshTimer || !currentGameId) {
    return;
  }

  autoRefreshTimer = window.setInterval(() => {
    refreshGameState().catch(() => {
      gameStatusValue.textContent = "Нет игры";
    });
  }, 2000);
}

refreshStateButton.addEventListener("click", () => run(async () => {
  await refreshGameState();
  setGameMessage("Шар обновлен.");
}));

markLastBallButton.addEventListener("click", () => run(async () => {
  if (!lastBallNumber) {
    throw new Error("Шар еще не выпал.");
  }

  const result = await markNumber(lastBallNumber);
  renderCard(result.card);
  setGameMessage(result.matched ? "Шар отмечен." : "Этого номера нет в карточке.");
}));

claimBingoButton.addEventListener("click", () => run(async () => {
  if (!currentCard) {
    throw new Error("Сначала создайте карточку.");
  }

  const claim = await submitWinnerClaim();
  setGameMessage(`Заявка отправлена: ${claim.status}.`);
}));

renderGameId();
if (currentGameId) {
  refreshGameState().then(startAutoRefresh).catch(() => {
    setGameMessage("Создайте карточку, когда хост запустит игру.", "is-success");
    startAutoRefresh();
  });
} else {
  setGameMessage("Сначала откройте лобби и создайте комнату.", "is-error");
}
