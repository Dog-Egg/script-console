import axios from "axios";
import { message } from "antd";
import { basename } from "path";

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

export function getDirectory() {
  return request({
    url: "/directory",
  });
}

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
    url: `/fs`,
    params: { path },
  });
}

export function updateFile(path, { content, name }) {
  const formData = new FormData();
  if (content) formData.append("content", content);
  if (name) formData.append("name", name);
  return request({
    url: `/fs`,
    method: "PUT",
    params: { path },
    data: formData,
  });
}

export function makeFile(path, isDir = false) {
  const formData = new FormData();
  formData.append("path", path);
  if (isDir) {
    formData.append("t", "d");
  }
  return request({
    url: "/fs",
    method: "POST",
    data: formData,
  });
}

export function removeFile(path) {
  const formData = new FormData();
  formData.append("path", path);
  return request({
    url: "/fs",
    method: "DELETE",
    data: formData,
  });
}

export function uploadFile(file, dir) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("dir", dir);
  return request({
    url: "/upload",
    method: "POST",
    data: formData,
  });
}

export function downloadFile(path) {
  request({
    url: "/download",
    params: { path },
    responseType: "blob",
  }).then((resp) => {
    const blob = new Blob([resp.data]);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = basename(path);
    a.click();
  });
}
