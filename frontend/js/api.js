const API_URL = "http://localhost:8000";

function getToken() {
  return localStorage.getItem("token");
}

function setToken(token) {
  localStorage.setItem("token", token);
}

function removeToken() {
  localStorage.removeItem("token");
  localStorage.removeItem("is_admin");
}

function authHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${getToken()}`,
  };
}

async function request(method, path, body = null, auth = true) {
  const options = {
    method,
    headers: auth
      ? authHeaders()
      : { "Content-Type": "application/json" },
  };
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(API_URL + path, options);

  if (res.status === 401) {
    removeToken();
    window.location.href = "/frontend/login.html";
    return;
  }

  if (res.status === 204) return null;

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Ошибка запроса");
  return data;
}

// Auth
const api = {
  register: (data) => request("POST", "/auth/register", data, false),
  login: (data) => request("POST", "/auth/login", data, false),

  // Products
  getProducts: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request("GET", `/products/?${q}`);
  },
  createProduct: (data) => request("POST", "/products/", data),
  updateProduct: (id, data) => request("PUT", `/products/${id}`, data),
  deleteProduct: (id) => request("DELETE", `/products/${id}`),

  // Cart
  getCart: () => request("GET", "/cart/"),
  addToCart: (items) => request("POST", "/cart/items", items),
  updateCartItem: (id, quantity) =>
    request("PATCH", `/cart/items/${id}`, { quantity }),
  removeCartItem: (id) => request("DELETE", `/cart/items/${id}`),
  clearCart: () => request("DELETE", "/cart/"),

  // Orders
  checkout: () => request("POST", "/orders/"),
  getOrders: () => request("GET", "/orders/"),
  updateOrderStatus: (id, status) =>
    request("PATCH", `/orders/${id}/status`, { status }),

  // Analytics
  getSummary: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request("GET", `/analytics/summary?${q}`);
  },
  getTopProducts: () => request("GET", "/analytics/top-products"),
  getCategories: () => request("GET", "/analytics/categories"),
  getDynamics: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request("GET", `/analytics/dynamics?${q}`);
  },
};
