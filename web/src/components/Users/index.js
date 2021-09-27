import {
  AutoComplete,
  Button,
  Form,
  Input,
  Modal,
  Popconfirm,
  Table,
  Tag,
} from "antd";
import { getUsers, delUser, addUser } from "../../api";
import React from "react";
import "./style.scss";
import { PlusOutlined } from "@ant-design/icons";
import { UserContext } from "../../ctx";
import uniq from "lodash/uniq";

export default function Users() {
  const [users, setUsers] = React.useState([]);
  React.useEffect(() => {
    getTableData();
  }, []);

  function getTableData() {
    getUsers().then((resp) => {
      const users = resp.data["users"];
      setUsers(users);
      const groups = users.map((i) => i.group).filter((i) => !!i);
      setGroupOptions(uniq(groups));
    });
  }

  const currentUser = React.useContext(UserContext);

  const [form] = Form.useForm();
  const [formModalVisible, setFormModalVisible] = React.useState(false);
  const [formModalLoading, setFormModalLoading] = React.useState(false);
  const [groupOptions, setGroupOptions] = React.useState([]);

  return (
    <div className="users">
      <header>
        <Button
          icon={<PlusOutlined />}
          type="primary"
          style={{ marginLeft: "auto", display: "block" }}
          onClick={() => {
            setFormModalVisible(true);
          }}
        >
          新增用户
        </Button>
      </header>
      <main>
        <Table dataSource={users} pagination={false} rowKey="id">
          <Table.Column
            title="姓名"
            dataIndex="real_name"
            render={(text, record) => (
              <span>
                {text}
                {record.id === currentUser.id && (
                  <Tag style={{ marginLeft: 10 }} color="success">
                    我
                  </Tag>
                )}
              </span>
            )}
          />
          <Table.Column title="令牌" dataIndex="token" />
          <Table.Column title="组" dataIndex="group" />
          <Table.Column
            render={(text, record) => (
              <>
                <Popconfirm
                  title="确定删除？"
                  onConfirm={() => {
                    delUser(record.id).then(() => {
                      getTableData();
                    });
                  }}
                >
                  <Button size="small" type="link" danger>
                    删除
                  </Button>
                </Popconfirm>
              </>
            )}
          />
        </Table>
      </main>

      <Modal
        title="新增用户"
        visible={formModalVisible}
        onCancel={() => {
          setFormModalVisible(false);
        }}
        onOk={() => {
          form.submit();
        }}
        afterClose={() => {
          form.resetFields();
        }}
        confirmLoading={formModalLoading}
      >
        <Form
          form={form}
          labelCol={{ span: 4 }}
          onFinish={(values) => {
            setFormModalLoading(true);
            addUser(values)
              .then(() => {
                setFormModalVisible(false);
                getTableData();
              })
              .finally(() => {
                setFormModalLoading(false);
              });
          }}
        >
          <Form.Item
            label="姓名"
            name="real_name"
            rules={[{ required: true, whitespace: true }]}
          >
            <Input />
          </Form.Item>
          <Form.Item label="组" name="group">
            <AutoComplete options={groupOptions.map((i) => ({ value: i }))} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
