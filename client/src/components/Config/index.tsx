import "./style.scss";
import React from "react";
import Panel from "../Panel";
import {
  Alert,
  Button,
  Collapse,
  Form,
  Input,
  message,
  Select,
  Space,
} from "antd";
import {
  DownCircleOutlined,
  MinusCircleOutlined,
  PlusOutlined,
  UpCircleOutlined,
} from "@ant-design/icons";
import { getConfig, updateConfig } from "../../api";

const requiredRule = [
  { required: true, message: "" },
  { whitespace: true, message: "" },
];

const Config = () => {
  const [form] = Form.useForm();

  const [configResponse, setConfigResponse] = React.useState<any>();
  React.useEffect(() => {
    getConfig().then((resp) => {
      setConfigResponse(resp.data);
    });
  }, []);

  React.useEffect(() => {
    if (configResponse) {
      form.setFieldsValue(configResponse.data);
    }
  }, [configResponse, form]);

  function onFinish(values: any) {
    setUpdateLoading(true);
    updateConfig(values)
      .then((resp) => {
        setConfigResponse(resp.data);
      })
      .then(() => {
        void message.success("保存成功");
      })
      .finally(() => {
        setUpdateLoading(false);
      });
  }

  const [updateLoading, setUpdateLoading] = React.useState(false);

  return (
    <Panel title="配置项">
      {configResponse && (
        <>
          {configResponse.error && (
            <Alert
              style={{ marginBottom: "24px" }}
              type="error"
              message="配置文件解析失败，可手动修改配置文件，或者在该页面重新设置并保存！"
              showIcon
              closable
            />
          )}

          <Form
            form={form}
            labelCol={{ span: 6 }}
            onFinish={onFinish}
            scrollToFirstError
          >
            <Space direction="vertical" style={{ display: "flex" }} size={20}>
              <Collapse defaultActiveKey="1">
                <Collapse.Panel header="执行脚本" key="1">
                  <Form.List name="commands">
                    {(fields, { add, remove, move }) => (
                      <>
                        {fields.map(({ key, name }, index) => (
                          <React.Fragment key={key}>
                            <div className="config-item">
                              <Form.Item
                                label="匹配模式"
                                name={[name, "pattern"]}
                                rules={[...requiredRule]}
                              >
                                <Input placeholder="正则表达式，如：\.js$、\.sh$" />
                              </Form.Item>
                              <Form.Item
                                label="执行程序"
                                name={[name, "program"]}
                                rules={[...requiredRule]}
                              >
                                <Input placeholder="如：node、/bin/bash" />
                              </Form.Item>
                              <Form.Item label="环境变量">
                                <Form.List name={[name, "environments"]}>
                                  {(fields, { add, remove }) => (
                                    <>
                                      {fields.map(({ key, name }) => (
                                        <Space
                                          key={key}
                                          style={{ display: "flex" }}
                                          align="baseline"
                                        >
                                          <Form.Item
                                            name={[name, "name"]}
                                            rules={[...requiredRule]}
                                          >
                                            <Input placeholder="变量名" />
                                          </Form.Item>
                                          <Form.Item
                                            name={[name, "value"]}
                                            rules={[...requiredRule]}
                                          >
                                            <Input placeholder="值" />
                                          </Form.Item>
                                          <MinusCircleOutlined
                                            style={{ color: "#777" }}
                                            onClick={() => remove(name)}
                                          />
                                        </Space>
                                      ))}
                                      <Button
                                        type="dashed"
                                        icon={<PlusOutlined />}
                                        onClick={() => add()}
                                        block
                                      >
                                        新增环境变量
                                      </Button>
                                    </>
                                  )}
                                </Form.List>
                              </Form.Item>
                              <div className="config-item-operators">
                                <UpCircleOutlined
                                  onClick={() => move(index, index - 1)}
                                  disabled={fields.length < 2 || index === 0}
                                />
                                <DownCircleOutlined
                                  onClick={() => move(index, index + 1)}
                                  disabled={
                                    fields.length < 2 ||
                                    index + 1 === fields.length
                                  }
                                />
                                <MinusCircleOutlined
                                  onClick={() => remove(name)}
                                />
                              </div>
                            </div>
                            <div className="config-divider" />
                          </React.Fragment>
                        ))}
                        <Button
                          type="dashed"
                          icon={<PlusOutlined />}
                          onClick={() => add()}
                          block
                        >
                          新增
                        </Button>
                      </>
                    )}
                  </Form.List>
                </Collapse.Panel>
              </Collapse>

              <Collapse defaultActiveKey="1">
                <Collapse.Panel header="使用权限" key="1">
                  <Form.List name="access">
                    {(fields, { add, remove, move }) => (
                      <>
                        {fields.map(({ key, name }, index) => (
                          <React.Fragment key={key}>
                            <div className="config-item">
                              <Form.Item
                                label="匹配模式"
                                name={[name, "pattern"]}
                                rules={[...requiredRule]}
                              >
                                <Input placeholder="正则表达式" />
                              </Form.Item>
                              <Form.Item label="用户组" name={[name, "groups"]}>
                                <Select mode="tags" />
                              </Form.Item>
                              <div className="config-item-operators">
                                <UpCircleOutlined
                                  onClick={() => move(index, index - 1)}
                                  disabled={fields.length < 2 || index === 0}
                                />
                                <DownCircleOutlined
                                  onClick={() => move(index, index + 1)}
                                  disabled={
                                    fields.length < 2 ||
                                    index + 1 === fields.length
                                  }
                                />
                                <MinusCircleOutlined
                                  onClick={() => remove(name)}
                                />
                              </div>
                            </div>
                            <div className="config-divider" />
                          </React.Fragment>
                        ))}
                        <Button
                          type="dashed"
                          icon={<PlusOutlined />}
                          onClick={() => add()}
                          block
                        >
                          新增
                        </Button>
                      </>
                    )}
                  </Form.List>
                </Collapse.Panel>
              </Collapse>

              <Collapse defaultActiveKey="1">
                <Collapse.Panel header="控制台" key="1">
                  <div className="config-item">
                    <Form.Item label="shell" name={["console", "shell"]}>
                      <Input placeholder="/bin/bash" />
                    </Form.Item>
                    <Form.Item label="环境变量">
                      <Form.List name={["console", "environments"]}>
                        {(fields, { add, remove }) => (
                          <>
                            {fields.map(({ key, name }) => (
                              <Space
                                key={key}
                                style={{ display: "flex" }}
                                align="baseline"
                              >
                                <Form.Item
                                  name={[name, "name"]}
                                  rules={[...requiredRule]}
                                >
                                  <Input placeholder="变量名" />
                                </Form.Item>
                                <Form.Item
                                  name={[name, "value"]}
                                  rules={[...requiredRule]}
                                >
                                  <Input placeholder="值" />
                                </Form.Item>
                                <MinusCircleOutlined
                                  style={{ color: "#777" }}
                                  onClick={() => remove(name)}
                                />
                              </Space>
                            ))}
                            <Button
                              type="dashed"
                              icon={<PlusOutlined />}
                              onClick={() => add()}
                              block
                            >
                              新增环境变量
                            </Button>
                          </>
                        )}
                      </Form.List>
                    </Form.Item>
                  </div>
                </Collapse.Panel>
              </Collapse>

              <Button
                htmlType="submit"
                type="primary"
                size="large"
                block
                loading={updateLoading}
              >
                保存
              </Button>
            </Space>
          </Form>
        </>
      )}
    </Panel>
  );
};

export default Config;
