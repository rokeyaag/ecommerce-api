const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const registerUser = async (username, email, password) => {
  const res = await fetch(`${BASE_URL}/api/auth/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password }),
  });
  return res.json();
};

export const loginUser = async (username, password) => {
  const res = await fetch(`${BASE_URL}/api/auth/token/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  return res.json();
};

export const getProducts = async () => {
  const res = await fetch(`${BASE_URL}/api/products/`);
  return res.json();
};

export const createOrder = async (orderData, token) => {
  const res = await fetch(`${BASE_URL}/api/orders/create/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(orderData),
  });
  return res.json();
};

export const getOrders = async (token) => {
  const res = await fetch(`${BASE_URL}/api/orders/`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  return res.json();
};

export const getCart = async (token) => {
  const res = await fetch(`${BASE_URL}/api/cart/`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  return res.json();
};

export const addToCart = async (productId, quantity, token) => {
  const res = await fetch(`${BASE_URL}/api/cart/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ product_id: productId, quantity }),
  });
  return res.json();
};

export const getToken = () => localStorage.getItem('access_token');
export const setToken = (token) => localStorage.setItem('access_token', token);
export const removeToken = () => localStorage.removeItem('access_token');
export const isLoggedIn = () => !!getToken();