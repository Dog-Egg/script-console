import request from "./_request";

export function signIn(token) {
  const formData = new FormData();
  formData.append("token", token);
  return request({
    url: "/sign",
    method: "POST",
    data: formData,
  });
}

export function signOut() {
  return request({
    url: "/sign",
    method: "DELETE",
  });
}

export function getCurrentUser() {
  return request({
    url: "/me",
  });
}

export function getUsers() {
  return request({
    url: "/users",
  });
}

export function addUser(data) {
  const formData = new FormData();
  Object.entries(data).forEach(([key, val]) => {
    if (val) {
      formData.append(key, val);
    }
  });
  return request({
    url: "/users",
    method: "POST",
    data: formData,
  });
}

export function delUser(uid) {
  return request({
    url: `/users/${uid}`,
    method: "DELETE",
  });
}
