import request from "./_request";
import { basename } from "path";

export function getDirectoryTree() {
  return request({
    url: "/file/tree",
  });
}

export function readFile(path) {
  return request({
    url: `/file/read`,
    params: { path },
  });
}

export function writeFile(path, content) {
  const formData = new FormData();
  if (content) formData.append("content", content);
  return request({
    url: `/file/write`,
    method: "POST",
    params: { path },
    data: formData,
  });
}

export function renameFile(source, target) {
  const formData = new FormData();
  formData.append("source", source);
  formData.append("target", target);
  return request({
    url: "/file/rename",
    method: "POST",
    data: formData,
  });
}

export function makeFile(path) {
  const formData = new FormData();
  formData.append("path", path);
  return request({
    url: "/file/mkfile",
    method: "POST",
    data: formData,
  });
}

export function makeDir(path) {
  const formData = new FormData();
  formData.append("path", path);
  return request({
    url: "/file/mkdir",
    method: "POST",
    data: formData,
  });
}

export function removeFile(path) {
  const formData = new FormData();
  formData.append("path", path);
  return request({
    url: "/file/remove",
    method: "POST",
    data: formData,
  });
}

export function uploadFile(file, dir) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("dir", dir);
  return request({
    url: "/file/upload",
    method: "POST",
    data: formData,
  });
}

export function downloadFile(path) {
  request({
    url: "/file/download",
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
