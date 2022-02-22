import "./style.scss";
import React from "react";
import { CloseOutlined } from "@ant-design/icons";

interface Props {
  title?: string;
  closeable?: boolean;
  onClose?: () => void;
}

const Toolbar: React.FC<Props> = function (props) {
  return (
    <div className={`toolbar`}>
      {props.title && <span>{props.title}:</span>}
      {props.children}
      {props.closeable && (
        <div className="toolbar-close" onClick={() => props.onClose?.()}>
          <CloseOutlined />
        </div>
      )}
    </div>
  );
};

export default Toolbar;
