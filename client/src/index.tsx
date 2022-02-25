import React from "react";
import ReactDOM from "react-dom";
import "./styles/index.scss";
import App from "./App";
import reportWebVitals from "./reportWebVitals";
import "antd/dist/antd.css";
import { UserContext } from "./ctx";
import { getCurrentUser } from "./api";
import { Spin, ConfigProvider } from "antd";
import zhCN from "antd/lib/locale/zh_CN";

function Entry() {
  const [currentUser, setCurrentUser] = React.useState();
  React.useEffect(() => {
    getCurrentUser().then((resp) => {
      const user = resp.data;
      setCurrentUser({
        ...user,
        isAdmin: user.group === "admin",
      });
    });
  }, []);

  return currentUser ? (
    <UserContext.Provider value={currentUser}>
      <ConfigProvider locale={zhCN}>
        <App />
      </ConfigProvider>
    </UserContext.Provider>
  ) : (
    <Spin
      size="large"
      style={{
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
      }}
    />
  );
}

ReactDOM.render(<Entry />, document.getElementById("root"));

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
