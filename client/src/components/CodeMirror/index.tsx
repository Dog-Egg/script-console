import React from "react";
import { IUnControlledCodeMirror, UnControlled } from "react-codemirror2";
import "codemirror/lib/codemirror.css";
import "./style.css";

const CodeMirror: React.FC<IUnControlledCodeMirror> = (props) => {
  const [importedMode, setImportedMode] = React.useState(false);
  const mode = props.options?.mode;

  React.useEffect(() => {
    if (!mode) return;

    import(`codemirror/mode/${mode}/${mode}.js`).finally(() => {
      setImportedMode(true);
    });
  }, [mode]);

  if (!mode || importedMode) {
    return <UnControlled {...props} />;
  }
  return <div />;
};

export default CodeMirror;
