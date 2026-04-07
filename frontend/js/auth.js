function requireAuth() {
  if (!getToken()) {
    window.location.href = "/frontend/login.html";
  }
}

function requireAdmin() {
  if (!getToken() || localStorage.getItem("is_admin") !== "true") {
    window.location.href = "/frontend/index.html";
  }
}

function logout() {
  removeToken();
  window.location.href = "/frontend/login.html";
}
