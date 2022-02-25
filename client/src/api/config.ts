import request from "./_request";

export function getConfig() {
  return request({
    url: "/config",
  });
}

export function updateConfig(data: any) {
  return request({
    url: "/config",
    method: "PUT",
    data,
  });
}
