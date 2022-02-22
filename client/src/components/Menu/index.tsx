import React, { useContext, useState } from "react";
import { Form, Menu as AntMenu, Modal, Input } from "antd";
import Icon, {
  GithubOutlined,
  HomeOutlined,
  LoginOutlined,
  LogoutOutlined,
  TeamOutlined,
} from "@ant-design/icons";
import { ReactComponent as TerminalSvg } from "../../icons/terminal.svg";
import { signIn, signOut } from "../../api";
import { UserContext } from "../../ctx";
import "./style.scss";

enum menuItemNames {
  WORKBENCH = "1",
  USERS = "2",
  SIGN_IN = "3",
  SIGN_OUT = "4",
  CONSOLE = "5",
}

interface Props {
  onClickMenuItem: (name: string, selected: () => void) => void;
  defaultItemName: menuItemNames;
}

interface MenuComponent extends React.FC<Props> {
  itemNames: typeof menuItemNames;
}

const Menu: MenuComponent = (props) => {
  const currentUser = useContext(UserContext);

  const [menuSelectedName, setMenuSelectedName] = useState<string>(
    props.defaultItemName
  );

  // token
  const [tokenModalVisible, setTokenModalVisible] = useState(false);
  const [tokenModalLoading, setTokenModalLoading] = useState(false);
  const [tokenForm] = Form.useForm();

  return (
    <div className="menu">
      <AntMenu
        mode="inline"
        inlineCollapsed
        selectedKeys={[menuSelectedName]}
        onClick={({ key }) => {
          props.onClickMenuItem(key, () => setMenuSelectedName(key));
        }}
      >
        <AntMenu.Item icon={<HomeOutlined />} key={menuItemNames.WORKBENCH} />
        {currentUser.isAdmin && (
          <>
            <AntMenu.Item icon={<TeamOutlined />} key={menuItemNames.USERS} />
            <AntMenu.Item
              icon={<Icon component={TerminalSvg} />}
              key={menuItemNames.CONSOLE}
            />
          </>
        )}
        {currentUser.anonymous ? (
          <AntMenu.Item
            icon={<LoginOutlined />}
            key={menuItemNames.SIGN_IN}
            onClick={() => setTokenModalVisible(true)}
          />
        ) : (
          <AntMenu.Item
            icon={<LogoutOutlined />}
            key={menuItemNames.SIGN_OUT}
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
      </AntMenu>
      <a className="github" href="https://github.com/Dog-Egg/script-console">
        <GithubOutlined />
      </a>

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
};

Menu.itemNames = menuItemNames;

export default Menu;
