const navLogoutButton = document.querySelector("#navLogoutButton");
const navUserName = document.querySelector("#navUserName");
const navLinks = document.querySelectorAll(".side-nav-link");

function readNavUser() {
  try {
    return JSON.parse(localStorage.getItem("bingo_user") || "null");
  } catch {
    return null;
  }
}

function clearNavSession() {
  localStorage.removeItem("bingo_access_token");
  localStorage.removeItem("bingo_user");
  window.location.href = "./login.html";
}

function markCurrentNavLink() {
  const currentPage = window.location.pathname.split("/").pop();

  navLinks.forEach((link) => {
    const linkPage = link.getAttribute("href")?.split("/").pop();
    link.classList.toggle("is-active", linkPage === currentPage);
  });
}

function renderNavUser() {
  const user = readNavUser();
  if (navUserName && user?.username) {
    navUserName.textContent = user.username;
  }
}

if (navLogoutButton) {
  navLogoutButton.addEventListener("click", clearNavSession);
}

markCurrentNavLink();
renderNavUser();
