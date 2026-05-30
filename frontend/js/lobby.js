const LOBBY_API_URL = "http://127.0.0.1:8003";
const GAME_PAGE_URL = "./game.html";

const createRoomButton = document.querySelector("#createRoomButton");
const joinRoomForm = document.querySelector("#joinRoomForm");
const joinRoomIdInput = document.querySelector("#joinRoomIdInput");
const startRoomButton = document.querySelector("#startRoomButton");
const lobbyMessage = document.querySelector("#lobbyMessage");
const roomStatus = document.querySelector("#roomStatus");
const roomIdValue = document.querySelector("#roomIdValue");
const roomHostValue = document.querySelector("#roomHostValue");
const playerList = document.querySelector("#playerList");
const openGameLink = document.querySelector("#openGameLink");

let currentRoom = null;

function getToken() {
  return localStorage.getItem("bingo_access_token");
}

function clearAuthSession() {
  localStorage.removeItem("bingo_access_token");
  localStorage.removeItem("bingo_user");
}

function setLobbyMessage(text, type = "is-success") {
  lobbyMessage.classList.remove("is-error", "is-success");
  lobbyMessage.textContent = text;
  lobbyMessage.classList.add(type);
}

function isNumericId(value) {
  return /^[1-9]\d*$/.test(String(value).trim());
}

function statusLabel(status) {
  return {
    waiting: "Ожидание",
    active: "Игра идет",
    finished: "Завершена",
  }[status] || status;
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

async function createRoom() {
  const response = await fetch(`${LOBBY_API_URL}/rooms`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  return readResponse(response);
}

async function joinRoom(roomId) {
  const response = await fetch(`${LOBBY_API_URL}/rooms/${encodeURIComponent(roomId)}/join`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  return readResponse(response);
}

async function loadRoom(roomId) {
  const response = await fetch(`${LOBBY_API_URL}/rooms/${encodeURIComponent(roomId)}`);
  return readResponse(response);
}

async function startRoom(roomId) {
  const response = await fetch(`${LOBBY_API_URL}/rooms/${encodeURIComponent(roomId)}/start`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  return readResponse(response);
}

function roomUrl(roomId) {
  return `${GAME_PAGE_URL}?game_id=${encodeURIComponent(roomId)}`;
}

function syncRoom(room) {
  currentRoom = room;
  localStorage.setItem("bingo_game_id", String(room.id));
  renderRoom(room);
}

function renderRoom(room) {
  roomStatus.textContent = statusLabel(room.status);
  roomIdValue.textContent = room.id;
  roomHostValue.textContent = `Хост: ${room.host_user_id}`;
  joinRoomIdInput.value = room.id;

  playerList.replaceChildren();
  room.players.forEach((player) => {
    const item = document.createElement("div");
    item.className = "lobby-player";
    item.innerHTML = `
      <strong>${player.user_id}</strong>
      <span>${new Date(player.joined_at).toLocaleString()}</span>
    `;
    playerList.appendChild(item);
  });

  startRoomButton.disabled = room.status !== "waiting";
  openGameLink.href = roomUrl(room.id);
  openGameLink.setAttribute("aria-disabled", "false");
}

async function withLobbyAction(action) {
  try {
    await action();
  } catch (error) {
    setLobbyMessage(error.message, "is-error");
  }
}

createRoomButton.addEventListener("click", () => withLobbyAction(async () => {
  setLobbyMessage("Создаем комнату...");
  syncRoom(await createRoom());
  setLobbyMessage("Комната создана. Код уже сохранен для карточки.");
}));

joinRoomForm.addEventListener("submit", (event) => withLobbyAction(async () => {
  event.preventDefault();
  const roomId = joinRoomIdInput.value.trim();
  if (!isNumericId(roomId)) {
    throw new Error("Введите числовой код комнаты.");
  }

  setLobbyMessage("Входим в комнату...");
  syncRoom(await joinRoom(roomId));
  setLobbyMessage("Вы в комнате. Можно перейти к карточке.");
}));

startRoomButton.addEventListener("click", () => withLobbyAction(async () => {
  if (!currentRoom) {
    throw new Error("Сначала выберите комнату.");
  }

  setLobbyMessage("Запускаем игру...");
  syncRoom(await startRoom(currentRoom.id));
  setLobbyMessage("Игра запущена. Шары появятся на странице карточки.");
}));

const savedGameId = localStorage.getItem("bingo_game_id");
if (isNumericId(savedGameId)) {
  joinRoomIdInput.value = savedGameId;
  withLobbyAction(async () => {
    syncRoom(await loadRoom(savedGameId));
    setLobbyMessage("Открыта последняя выбранная комната.");
  });
}
