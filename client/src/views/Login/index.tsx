import React from "react";
import { signIn } from "../../api";
import { history } from "../../utils";

const Login: React.FC = () => {
  const [token, setToken] = React.useState("");
  return (
    <div>
      <input
        type="text"
        onChange={(e) => {
          setToken(e.target.value);
        }}
      />
      <button
        onClick={() => {
          signIn(token).then(() => {
            history.replace("/");
          });
        }}
      >
        提交
      </button>
    </div>
  );
};

export default Login;
