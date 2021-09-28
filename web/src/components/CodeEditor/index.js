import { Modal, Spin } from "antd";
import React, { Suspense, useRef, useState } from "react";

const CodeMirror = React.lazy(() => import("../CodeMirror"));

export default function CodeEditor(props) {
  const [codeChanged, setCodeChanged] = useState(false);
  const codeMirrorRef = useRef();
  return (
    <Modal
      title={props.title}
      visible={props.visible}
      width={1000}
      style={{ top: "10vh" }}
      destroyOnClose
      maskClosable={false}
      onCancel={props.onCancel}
      afterClose={() => {
        setCodeChanged(false);
      }}
      okButtonProps={{ disabled: !codeChanged }}
      okText="保存"
      onOk={() => {
        const editor = codeMirrorRef.current["editor"];
        const content = editor.getValue();
        props.onOk(content);
      }}
    >
      <Suspense
        fallback={
          <div style={{ textAlign: "center" }}>
            <Spin />
          </div>
        }
      >
        <CodeMirror
          ref={codeMirrorRef}
          editorDidMount={(editor) => {
            setTimeout(() => {
              editor.refresh();
            }, 200);
          }}
          value={props.content}
          options={{
            lineNumbers: true,
            mode: props.mode,
          }}
          onChange={function (_, __, value) {
            setCodeChanged(value !== props.content);
          }}
        />
      </Suspense>
    </Modal>
  );
}
