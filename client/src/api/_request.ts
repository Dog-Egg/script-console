import axios, { AxiosError } from "axios";
import { message } from "antd";
import { history } from "../utils";

const request = axios.create({
  baseURL: "/api",
  timeout: 3000,
});

request.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    const response = error.response;
    if (response) {
      if (response.status === 401) {
        history.replace("/login");
      } else if (response.status === 403) {
        history.replace("/");
      } else {
        const errMessage = response.data.message;
        if (errMessage !== null) {
          void message.error(errMessage || error.message);
        }
      }
    } else {
      void message.error(error.message);
    }
    return Promise.reject(error);
  }
);

export default request;
