import { Modal, Spin } from "antd";
import React, { Suspense, useState, useMemo } from "react";
import { Editor } from "codemirror";

const CodeMirror = React.lazy(() => import("../CodeMirror"));

interface Props {
  title: string;
  visible: boolean;
  content: string;
  onCancel: () => void;
  onOk: (text: string) => void;
}

const CodeEditor: React.FC<Props> = (props) => {
  const [codeChanged, setCodeChanged] = useState(false);

  const [editor, setEditor] = useState<Editor>();

  const mode = useMemo<string | undefined>(() => {
    if (!props.title) return;

    const values = props.title.split(".");
    if (values.length < 2) return;

    const ext = values.pop() as string;
    return (
      {
        py: "python",
        js: "javascript",
        sh: "shell",
      }[ext] || ext
    );
  }, [props.title]);

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
        const content = editor!.getValue();
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
          editorDidMount={(editor) => {
            setEditor(editor);
            setTimeout(() => {
              editor.refresh();
            }, 200);
          }}
          value={props.content}
          options={{
            lineNumbers: true,
            mode,
          }}
          onChange={function (_, __, value) {
            setCodeChanged(value !== props.content);
          }}
        />
      </Suspense>
    </Modal>
  );
};

export default CodeEditor;
