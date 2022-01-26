import React, { useEffect, useRef, useState } from "react";
import {
  Resizable as BaseResizeable,
  ResizeCallbackData,
} from "react-resizable";
import "react-resizable/css/styles.css";
import "./style.scss";

type Size = number | string;
type ResizeHandleAxis = "s" | "w" | "e" | "n";

const Resizable: React.FC<{
  width?: Size;
  height?: Size;
  resizeHandleAxis: ResizeHandleAxis;
}> = (props) => {
  const [widthDelta, setWidthDelta] = useState<number>(0);
  const [heightDelta, setHeightDelta] = useState<number>(0);

  const [width, setWidth] = useState(props.width);
  const [height, setHeight] = useState(props.height);

  const onResize = (event: any, { size }: ResizeCallbackData) => {
    setWidthDelta(size.width);
    setHeightDelta(size.height);
    typeof props.width === "number" && setWidth(props.width + size.width);
    typeof props.height === "number" && setHeight(props.height + size.height);
  };

  const elementRef = useRef<HTMLDivElement>(null);
  useEffect(() => {}, []);

  return (
    <BaseResizeable
      width={widthDelta}
      height={heightDelta}
      onResize={onResize}
      maxConstraints={[Infinity, Infinity]}
      minConstraints={[-Infinity, -Infinity]}
      resizeHandles={[props.resizeHandleAxis]}
      handle={<MyHandle />}
    >
      <div ref={elementRef} style={{ width, height }}>
        {props.children}
      </div>
    </BaseResizeable>
  );
};

const MyHandleComponent: React.FC<any> = (props) => {
  const { handleAxis, innerRef, ...others } = props;
  return (
    <div
      ref={innerRef}
      className={`resizable-handle resizable-handle-${handleAxis}`}
      {...others}
    />
  );
};
const MyHandle = React.forwardRef((props, ref) => (
  <MyHandleComponent innerRef={ref} {...props} />
));

export default Resizable;
