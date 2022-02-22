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
        message.error(errMessage || error.message).then();
      }
    } else {
      message.error(error.message).then();
    }
    return Promise.reject(error);
  }
);

export default request;
