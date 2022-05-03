import "./style.scss";
import React, { useState } from "react";
import Console from "../../components/Console";
import Split from "../../components/Split";
import { UserContext } from "../../utils/ctx";
import { getCurrentUser, signOut } from "../../api";
import { Spin, Menu, Modal } from "antd";
import { Outlet } from "react-router-dom";
import Icon, {
  GithubOutlined,
  LoginOutlined,
  LogoutOutlined,
} from "@ant-design/icons";
import { history } from "../../utils";
import { useCurrentUser } from "../../utils/hooks";
import { ReactComponent as TerminalSvg } from "../../icons/terminal.svg";
import { useNavigate, useLocation } from "react-router-dom";

interface Props {
  routes: {
    metadata: { icon: React.ReactNode; admin?: boolean };
    path: string;
  }[];
}

const Home: React.FC<Props> = ({ routes }) => {
  const currentUser = useCurrentUser();
  const [enableConsole, setEnabledConsole] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="layout">
      <div className="layout-menu">
        <div className="menu">
          <Menu
            mode="inline"
            inlineCollapsed
            selectedKeys={[location.pathname]}
          >
            {routes.map((route) => {
              const { metadata } = route;
              if (metadata.admin && !currentUser.isAdmin) {
                return false;
              }
              return (
                <Menu.Item
                  icon={metadata.icon}
                  key={route.path}
                  onClick={() => {
                    navigate(route.path);
                  }}
                />
              );
            })}

            {/*console*/}
            {currentUser.isAdmin && (
              <Menu.Item
                icon={<Icon component={TerminalSvg} />}
                key="console"
                onClick={() => {
                  setEnabledConsole(true);
                }}
              />
            )}

            {/*sign*/}
            {currentUser.anonymous ? (
              <Menu.Item
                icon={<LoginOutlined />}
                onClick={() => history.push("/login")}
                key="signIn"
              />
            ) : (
              <Menu.Item
                key="signOut"
                icon={<LogoutOutlined />}
                onClick={() => {
                  Modal.confirm({
                    title: "确定注销？",
                    onOk() {
                      signOut().then(() => {
                        window.location.reload();
                      });
                    },
                  });
                }}
              />
            )}
          </Menu>
          <a
            className="github"
            href="https://github.com/Dog-Egg/script-console"
          >
            <GithubOutlined />
          </a>
        </div>
      </div>
      <Split
        className="layout-main"
        sizes={enableConsole ? [70, 30] : undefined}
        direction="vertical"
      >
        <div className="layout-main-part1">
          <Outlet />
        </div>
        {enableConsole && (
          <div className="layout-main-part2">
            <Console onClose={() => setEnabledConsole(false)} />
          </div>
        )}
      </Split>
    </div>
  );
};

const HomeWrapper: React.FC<Props> = (props) => {
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
      <Home {...props} />
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
};

export default HomeWrapper;
