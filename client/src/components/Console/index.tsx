import "./style.scss";
import React from "react";
import Terminal from "../Terminal";
import Toolbar from "../Toolbar";

interface Props {
  onClose?: () => void;
}

class Console extends React.Component<Props> {
  private terminal: Terminal | null;

  constructor(props: {}) {
    super(props);
    this.terminal = null;
  }

  componentDidMount() {
    this.terminal?.openWebSocket(`ws://${window.location.host}/ws/console`);
  }

  render() {
    return (
      <div className="console">
        <Toolbar title="Terminal" closeable onClose={this.props.onClose} />
        <Terminal ref={(term) => (this.terminal = term)} autoFocus />
      </div>
    );
  }
}

export default Console;
