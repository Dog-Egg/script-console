import React, { Suspense } from "react";
import {
  Route,
  Routes,
  unstable_HistoryRouter as HistoryRouter,
} from "react-router-dom";
import Home from "./views/Home";
import Login from "./views/Login";
import { history } from "./utils";
import Workbench from "./components/Workbench";
import { HomeOutlined, SettingOutlined, TeamOutlined } from "@ant-design/icons";
import { Spin } from "antd";

const Users = React.lazy(() => import("./components/Users"));
const Config = React.lazy(() => import("./components/Config"));

function withSuspense(Component: React.ReactNode) {
  return (
    <Suspense
      fallback={
        <Spin
          size="large"
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
          }}
        />
      }
    >
      {Component}
    </Suspense>
  );
}

const routes = [
  {
    path: "/",
    element: <Workbench />,
    metadata: {
      icon: <HomeOutlined />,
    },
  },
  {
    path: "/users",
    element: withSuspense(<Users />),
    metadata: {
      icon: <TeamOutlined />,
      admin: true,
    },
  },
  {
    path: "/config",
    element: withSuspense(<Config />),
    metadata: {
      icon: <SettingOutlined />,
      admin: true,
    },
  },
];

function App() {
  return (
    <HistoryRouter history={history}>
      <Routes>
        <Route path="/" element={<Home routes={routes} />}>
          {routes.map((route, index) => (
            <Route {...route} key={index} />
          ))}
        </Route>
        <Route path="login" element={<Login />} />
      </Routes>
    </HistoryRouter>
  );
}

export default App;
