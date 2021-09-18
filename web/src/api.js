import axios from "axios";
import { message } from "antd";

const request = axios.create({
  baseURL: "/api",
  timeout: 3000,
});

request.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const response = error.response;
    if (response) {
      const errMessage = response.data.message;
      if (errMessage !== null) {
        message.error(errMessage || error.message);
      }
    } else {
      message.error(error.message);
    }
    return Promise.reject(error);
  }
);

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

export function getFile(path) {
  return request({
    url: `/file`,
    params: { path },
  });
}

export function updateFile(path, content) {
  const formData = new FormData();
  formData.append("content", content);
  return request({
    url: `/file`,
    method: "PUT",
    params: { path },
    data: formData,
  });
}
