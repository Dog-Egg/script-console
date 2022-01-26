import "./App.scss";
import React, { useContext, useState } from "react";
import { Form, Input, Menu, Modal, Spin } from "antd";
import Icon, {
  GithubOutlined,
  TeamOutlined,
  HomeOutlined,
  LogoutOutlined,
  LoginOutlined,
} from "@ant-design/icons";
import { signIn, signOut } from "./api";
import { UserContext } from "./ctx";
import { ReactComponent as TerminalSvg } from "./icons/terminal.svg";

const Workbench = React.lazy(() => import("./components/Workbench"));
const Users = React.lazy(() => import("./components/Users"));

const asideItemNames = {
  HOME: "1",
  USERS: "2",
  SIGN_IN: "3",
  SIGN_OUT: "4",
  TERMINAL: "5",
};

function App() {
  const [tokenModalVisible, setTokenModalVisible] = useState(false);
  const [tokenModalLoading, setTokenModalLoading] = useState(false);

  const [asideSelectedName, setAsideSelectedName] = useState(
    asideItemNames.HOME
  );

  const currentUser = useContext(UserContext);

  const [tokenForm] = Form.useForm();

  return (
    <div className="app">
      <aside>
        <Menu
          mode="inline"
          inlineCollapsed
          selectedKeys={[asideSelectedName]}
          onClick={({ key }) => {
            if ([asideItemNames.HOME, asideItemNames.USERS].includes(key)) {
              setAsideSelectedName(key);
            }
          }}
        >
          <Menu.Item icon={<HomeOutlined />} key={asideItemNames.HOME} />
          {currentUser.isAdmin && (
            <>
              <Menu.Item icon={<TeamOutlined />} key={asideItemNames.USERS} />
              <Menu.Item
                icon={<Icon component={TerminalSvg} />}
                key={asideItemNames.TERMINAL}
              />
            </>
          )}
          {currentUser.anonymous ? (
            <Menu.Item
              icon={<LoginOutlined />}
              key={asideItemNames.SIGN_IN}
              onClick={() => setTokenModalVisible(true)}
            />
          ) : (
            <Menu.Item
              icon={<LogoutOutlined />}
              key={asideItemNames.SIGN_OUT}
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
        <a className="github" href="https://github.com/Dog-Egg/script-console">
          <GithubOutlined />
        </a>
      </aside>
      <main style={{ position: "relative" }}>
        <React.Suspense
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
          {
            {
              [asideItemNames.HOME]: <Workbench />,
              [asideItemNames.USERS]: <Users />,
            }[asideSelectedName]
          }
        </React.Suspense>
      </main>

      <Modal
        visible={tokenModalVisible}
        onCancel={() => {
          setTokenModalVisible(false);
        }}
        title="校验令牌"
        afterClose={() => {
          tokenForm.resetFields();
        }}
        confirmLoading={tokenModalLoading}
        onOk={() => {
          tokenForm.submit();
        }}
      >
        <Form
          form={tokenForm}
          onFinish={({ token }) => {
            setTokenModalLoading(true);
            signIn(token)
              .then(() => {
                window.location.reload();
              })
              .catch((err) => {
                const resp = err.response;
                tokenForm.setFields([
                  { name: "token", errors: [resp.data.errors.token] },
                ]);
              })
              .finally(() => {
                setTokenModalLoading(false);
              });
          }}
        >
          <Form.Item
            name="token"
            rules={[{ required: true, message: "请输入令牌" }]}
          >
            <Input.Password />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default App;
