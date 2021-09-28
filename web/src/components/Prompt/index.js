import { Input, Modal } from "antd";
import ReactDOM from "react-dom";
import { useState } from "react";

const mountNode = document.createElement("div");

export default function prompt(options) {
  return new Promise((resolve, reject) => {
    const prompt = (
      <Prompt
        {...options}
        onOk={resolve}
        onCancel={() => reject("prompt close")}
      />
    );
    ReactDOM.render(prompt, mountNode);
  });
}

function Prompt(props) {
  const [visible, setVisible] = useState(true);
  const [value, setValue] = useState("");
  const isOk = !!value.trim();

  function handleOk() {
    if (!isOk) return;
    props.onOk && props.onOk(value);
    setVisible(false);
  }

  return (
    <Modal
      title={props.title}
      visible={visible}
      closable={false}
      onCancel={() => {
        props.onCancel && props.onCancel();
        setVisible(false);
      }}
      afterClose={() => {
        ReactDOM.unmountComponentAtNode(mountNode);
      }}
      onOk={handleOk}
      okButtonProps={{ disabled: !isOk }}
    >
      <Input
        onPressEnter={handleOk}
        onChange={(e) => {
          setValue(e.target.value);
        }}
      />
    </Modal>
  );
}
