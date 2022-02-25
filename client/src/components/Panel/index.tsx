import "./style.scss";
import React from "react";

interface Props {
  title: string;
}

const Panel: React.FC<Props> = (props) => {
  return (
    <div className="panel">
      <h2 className="panel-title">{props.title}</h2>
      <div>{props.children}</div>
    </div>
  );
};

export default Panel;
