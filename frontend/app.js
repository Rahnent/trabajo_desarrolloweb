const log = (msg) => {
  document.getElementById("output").textContent = JSON.stringify(msg, null, 2);
};

async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  
  const res = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ username, password })
  });
  log(await res.json());
}

async function getMe() {
  const res = await fetch("/auth/me", { credentials: "include" });
  log(await res.json());
}

async function getProducts() {
  const res = await fetch("/api/products", { credentials: "include" });
  log(await res.json());
}

async function deleteProduct(id) {
  const res = await fetch(`/api/products/${id}`, {
    method: "DELETE",
    credentials: "include"
  });
  log(await res.json());
}

async function logout() {
  const res = await fetch("/auth/logout", {
    method: "POST",
    credentials: "include"
  });
  log(await res.json());
}