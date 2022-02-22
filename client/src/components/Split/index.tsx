import ReactSplit, { SplitProps } from "react-split";
import React from "react";
import "./style.scss";

const Split: React.FC<SplitProps> = (props) => {
  const gutter = (index: number, direction: string) => {
    const gutter = document.createElement("div");
    gutter.className = `gutter-wrapper`;
    gutter.innerHTML = `<div class="gutter gutter-${direction}"></div>`;
    return gutter;
  };
  return <ReactSplit {...props} gutterSize={0} gutter={gutter} />;
};

export default Split;
