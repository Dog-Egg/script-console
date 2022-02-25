import SplitJS from "split.js";
import React from "react";
import "./style.scss";
import isEqual from "lodash/isEqual";

interface Props {
  className?: string;
  sizes?: number[];
  direction?: SplitJS.Options["direction"];
}

const gutter = (index: number, direction: Props["direction"]) => {
  const gutter = document.createElement("div");
  gutter.className = `gutter-wrapper`;
  gutter.innerHTML = `<div class="gutter gutter-${direction}"></div>`;
  return gutter;
};

class Split extends React.Component<Props> {
  instance: SplitJS.Instance | null = null;
  parent: HTMLDivElement | null = null;
  sizes?: number[];

  private checkInstance() {
    const { sizes, ...rest } = this.props;

    if (!this.parent || isEqual(sizes, this.sizes)) return;

    if (sizes) {
      this.instance = SplitJS(
        Array.from(this.parent.children) as HTMLElement[],
        {
          sizes,
          gutter,
          gutterSize: 0,
          ...rest,
        }
      );
    } else {
      this.instance?.destroy();
    }
    this.sizes = sizes;
  }

  componentDidMount() {
    this.checkInstance();
  }

  componentDidUpdate() {
    this.checkInstance();
  }

  componentWillUnmount() {
    this.instance?.destroy();
  }

  render() {
    const { children, sizes, direction, ...rest } = this.props;
    return (
      <div
        ref={(parent) => {
          this.parent = parent;
        }}
        {...rest}
      >
        {children}
      </div>
    );
  }
}

export default Split;
