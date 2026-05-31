const LOBBY_API_URL = "";
const LOGIN_PAGE_URL = "./login.html";
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
const patternOptions = document.querySelector("#patternOptions");
const patternModal = document.querySelector("#patternModal");
const openPatternModalButton = document.querySelector("#openPatternModalButton");
const closePatternModalButton = document.querySelector("#closePatternModalButton");
const selectedPatternPreview = document.querySelector("#selectedPatternPreview");
const selectedPatternLabel = document.querySelector("#selectedPatternLabel");

let currentRoom = null;
let busy = false;
let selectedWinningPattern = "top_row";

const WINNING_PATTERNS = [
  { id: "top_row", label: "Верхняя строка", cells: [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]] },
  { id: "middle_row", label: "Средняя строка", cells: [[2, 0], [2, 1], [2, 2], [2, 3], [2, 4]] },
  { id: "bottom_row", label: "Нижняя строка", cells: [[4, 0], [4, 1], [4, 2], [4, 3], [4, 4]] },
  { id: "left_column", label: "Левый столбец", cells: [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]] },
  { id: "middle_column", label: "Средний столбец", cells: [[0, 2], [1, 2], [2, 2], [3, 2], [4, 2]] },
  { id: "right_column", label: "Правый столбец", cells: [[0, 4], [1, 4], [2, 4], [3, 4], [4, 4]] },
  { id: "main_diagonal", label: "Диагональ", cells: [[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]] },
  { id: "anti_diagonal", label: "Обратная диагональ", cells: [[0, 4], [1, 3], [2, 2], [3, 1], [4, 0]] },
  { id: "four_corners", label: "Углы", cells: [[0, 0], [0, 4], [4, 0], [4, 4]] },
  { id: "x_shape", label: "Крест X", cells: [[0, 0], [1, 1], [2, 2], [3, 3], [4, 4], [0, 4], [1, 3], [3, 1], [4, 0]] },
  { id: "plus_shape", label: "Плюс", cells: [[0, 2], [1, 2], [2, 0], [2, 1], [2, 2], [2, 3], [2, 4], [3, 2], [4, 2]] },
  { id: "small_frame", label: "Малая рамка", cells: [[1, 1], [1, 2], [1, 3], [2, 1], [2, 3], [3, 1], [3, 2], [3, 3]] },
];

function getToken() {
  return localStorage.getItem("bingo_access_token");
}

function clearAuthSession() {
  localStorage.removeItem("bingo_access_token");
  localStorage.removeItem("bingo_user");
}

function readCachedUser() {
  try {
    return JSON.parse(localStorage.getItem("bingo_user") || "null");
  } catch {
    return null;
  }
}

function decodeTokenPayload() {
  const token = getToken();
  if (!token) {
    return null;
  }

  try {
    const payload = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
}

function getCurrentUserId() {
  const payload = decodeTokenPayload();
  return payload?.sub ? String(payload.sub) : "";
}

function isHost() {
  return currentRoom?.host_user_id && currentRoom.host_user_id === getCurrentUserId();
}

function setLobbyMessage(text, type = "is-success") {
  lobbyMessage.classList.remove("is-error", "is-success");
  lobbyMessage.textContent = text;
  lobbyMessage.classList.add(type);
}

function isNumericId(value) {
  return /^[1-9]\d*$/.test(String(value || "").trim());
}

function statusLabel(status) {
  return {
    waiting: "Ожидание игроков",
    active: "Игра идет",
    finished: "Завершена",
  }[status] || status || "Неизвестно";
}

function getAuthHeaders() {
  const token = getToken();
  if (!token) {
    throw new Error("Нужно войти в аккаунт.");
  }

  const headers = { Authorization: `Bearer ${token}` };
  const cachedUser = readCachedUser();
  if (cachedUser?.username) {
    headers["X-User-Name"] = cachedUser.username;
  }
  return headers;
}

async function readResponse(response) {
  const data = await response.json().catch(() => ({}));

  if (response.status === 401) {
    clearAuthSession();
    throw new Error("Сессия истекла. Войдите заново.");
  }

  if (!response.ok) {
    throw new Error(data.detail || "Сервис комнат вернул ошибку.");
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
    headers: {
      ...getAuthHeaders(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ winning_pattern: selectedWinningPattern }),
  });
  return readResponse(response);
}

function roomUrl(roomId) {
  return `${GAME_PAGE_URL}?game_id=${encodeURIComponent(roomId)}`;
}

function renderEmptyRoom() {
  currentRoom = null;
  roomStatus.textContent = "Комната не выбрана";
  roomIdValue.textContent = "...";
  roomHostValue.textContent = "Хост: ...";
  playerList.replaceChildren();

  const empty = document.createElement("div");
  empty.className = "empty-state";
  empty.textContent = "Создайте комнату или войдите по коду.";
  playerList.appendChild(empty);

  startRoomButton.disabled = true;
  openGameLink.href = GAME_PAGE_URL;
  openGameLink.setAttribute("aria-disabled", "true");
  renderPatternOptions();
  renderSelectedPattern();
}

function syncRoom(room) {
  currentRoom = room;
  localStorage.setItem("bingo_game_id", String(room.id));
  renderRoom(room);
}

function renderRoom(room) {
  selectedWinningPattern = room.winning_pattern || selectedWinningPattern;
  roomStatus.textContent = statusLabel(room.status);
  roomIdValue.textContent = room.id;
  const host = room.players.find((player) => player.user_id === room.host_user_id);
  roomHostValue.textContent = `Хост: ${host?.display_name || room.host_user_id}`;
  joinRoomIdInput.value = room.id;

  playerList.replaceChildren();
  room.players.forEach((player) => {
    const item = document.createElement("div");
    item.className = "lobby-player";

    const name = document.createElement("strong");
    name.textContent = player.display_name || `Игрок ${player.user_id}`;

    const joinedAt = document.createElement("span");
    joinedAt.textContent = new Date(player.joined_at).toLocaleString("ru-RU");

    item.append(name, joinedAt);
    playerList.appendChild(item);
  });

  startRoomButton.disabled = busy || room.status !== "waiting" || !isHost();
  openGameLink.href = roomUrl(room.id);
  openGameLink.setAttribute("aria-disabled", "false");
  renderPatternOptions();
  renderSelectedPattern();
}

function setBusy(isBusy) {
  busy = isBusy;
  createRoomButton.disabled = isBusy;
  joinRoomForm.querySelectorAll("input, button").forEach((element) => {
    element.disabled = isBusy;
  });
  startRoomButton.disabled = isBusy || !currentRoom || currentRoom.status !== "waiting" || !isHost();
  openPatternModalButton.disabled = isBusy || (currentRoom && (currentRoom.status !== "waiting" || !isHost()));
  renderPatternOptions();
  renderSelectedPattern();
}

function patternCellKey(row, col) {
  return `${row}:${col}`;
}

function selectedPattern() {
  return WINNING_PATTERNS.find((pattern) => pattern.id === selectedWinningPattern) || WINNING_PATTERNS[0];
}

function renderPatternPreview(container, pattern) {
  container.replaceChildren();

  const selectedCells = new Set(pattern.cells.map(([row, col]) => patternCellKey(row, col)));
  for (let row = 0; row < 5; row += 1) {
    for (let col = 0; col < 5; col += 1) {
      const dot = document.createElement("span");
      dot.className = selectedCells.has(patternCellKey(row, col)) ? "pattern-dot is-selected" : "pattern-dot";
      container.appendChild(dot);
    }
  }
}

function renderSelectedPattern() {
  const pattern = selectedPattern();
  selectedPatternLabel.textContent = pattern.label;
  renderPatternPreview(selectedPatternPreview, pattern);
}

function renderPatternOptions() {
  patternOptions.replaceChildren();

  WINNING_PATTERNS.forEach((pattern) => {
    const option = document.createElement("button");
    option.className = "pattern-option";
    option.type = "button";
    option.disabled = busy || (currentRoom && (currentRoom.status !== "waiting" || !isHost()));
    option.setAttribute("aria-pressed", String(pattern.id === selectedWinningPattern));

    const preview = document.createElement("span");
    preview.className = "pattern-preview";
    renderPatternPreview(preview, pattern);

    const label = document.createElement("strong");
    label.textContent = pattern.label;

    option.append(preview, label);
    option.addEventListener("click", () => {
      selectedWinningPattern = pattern.id;
      closePatternModal();
      renderPatternOptions();
      renderSelectedPattern();
    });
    patternOptions.appendChild(option);
  });
}

function openPatternModal() {
  if (openPatternModalButton.disabled) {
    return;
  }
  patternModal.classList.remove("is-hidden");
}

function closePatternModal() {
  patternModal.classList.add("is-hidden");
}

async function withLobbyAction(action) {
  if (busy) {
    return;
  }

  setBusy(true);
  try {
    await action();
  } catch (error) {
    setLobbyMessage(error.message, "is-error");
    if (error.message.includes("войти") || error.message.includes("Сессия")) {
      setTimeout(() => {
        window.location.href = LOGIN_PAGE_URL;
      }, 650);
    }
  } finally {
    setBusy(false);
  }
}

createRoomButton.addEventListener("click", () => withLobbyAction(async () => {
  setLobbyMessage("Создаем комнату...");
  syncRoom(await createRoom());
  setLobbyMessage("Комната создана. Передайте код другим игрокам.");
}));

joinRoomForm.addEventListener("submit", (event) => withLobbyAction(async () => {
  event.preventDefault();
  const roomId = joinRoomIdInput.value.trim();
  if (!isNumericId(roomId)) {
    throw new Error("Введите числовой код комнаты.");
  }

  setLobbyMessage("Входим в комнату...");
  syncRoom(await joinRoom(roomId));
  setLobbyMessage("Вы в комнате. Когда хост начнет игру, переходите к карточке.");
}));

startRoomButton.addEventListener("click", () => withLobbyAction(async () => {
  if (!currentRoom) {
    throw new Error("Сначала выберите комнату.");
  }

  setLobbyMessage("Запускаем игру...");
  syncRoom(await startRoom(currentRoom.id));
  setLobbyMessage("Игра запущена. Теперь можно открыть карточку.");
}));

openPatternModalButton.addEventListener("click", openPatternModal);
closePatternModalButton.addEventListener("click", closePatternModal);
patternModal.addEventListener("click", (event) => {
  if (event.target === patternModal) {
    closePatternModal();
  }
});

renderEmptyRoom();

const savedGameId = localStorage.getItem("bingo_game_id");
if (isNumericId(savedGameId)) {
  joinRoomIdInput.value = savedGameId;
  withLobbyAction(async () => {
    syncRoom(await loadRoom(savedGameId));
    setLobbyMessage("Открыта последняя выбранная комната.");
  });
}
