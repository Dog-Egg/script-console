import React from "react";

import "xterm/css/xterm.css";
import { Terminal as _Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import { SearchAddon } from "xterm-addon-search";
import { WebLinksAddon } from "xterm-addon-web-links";

import elementResizeDetectorMaker from "element-resize-detector";

interface Props {
  onWebSocketClose?: () => void;
  onWebSocketOpen?: () => void;
}

class Terminal extends React.Component<Props> {
  private readonly elementRef: React.RefObject<HTMLDivElement>;
  private readonly terminal: _Terminal;
  private readonly fitAddon: FitAddon;
  private readonly searchAddon: SearchAddon;
  private readonly webLinksAddon: WebLinksAddon;
  private resizer?: elementResizeDetectorMaker.Erd;
  private ws?: WebSocket;

  constructor(props: Props) {
    super(props);

    this.elementRef = React.createRef();

    this.terminal = new _Terminal({
      cursorBlink: true,
      tabStopWidth: 4,
      convertEol: true,
      theme: {
        selection: "rgb(252,229,70)",
      },
    });

    this.terminal.onData((data) => {
      this.messageWebSocket(data);
    });

    // addon
    this.fitAddon = new FitAddon();
    this.searchAddon = new SearchAddon();
    this.webLinksAddon = new WebLinksAddon();

    this.terminal.loadAddon(this.fitAddon);
    this.terminal.loadAddon(this.searchAddon);
    this.terminal.loadAddon(this.webLinksAddon);
  }

  componentDidMount() {
    if (!this.elementRef.current) return;

    this.terminal.open(this.elementRef.current);
    this.fitAddon.fit(); // 在 onresize 中首次调用会出现闪烁

    // 监听组件元素大小变化
    this.resizer = elementResizeDetectorMaker({
      callOnAdd: false,
    });
    this.resizer.listenTo(this.elementRef.current, () => {
      this.fitAddon.fit();
    });
  }

  componentWillUnmount() {
    this.terminal.dispose();
    this.fitAddon.dispose();
    this.searchAddon.dispose();
    this.webLinksAddon.dispose();

    this.ws && this.ws.close();

    if (this.resizer && this.elementRef.current) {
      this.resizer.uninstall(this.elementRef.current);
    }
  }

  writeln(value: string) {
    this.terminal.writeln(value);
  }

  searchNext(value: string) {
    this.searchAddon.findNext(value);
  }

  searchPrevious(value: string) {
    this.searchAddon.findPrevious(value);
  }

  clearSelection() {
    this.terminal.clearSelection();
  }

  openWebSocket(url: string) {
    if (this.ws) this.ws.close(4000);
    this.ws = new WebSocket(url);

    this.ws.addEventListener("open", () => {
      this.props.onWebSocketOpen && this.props.onWebSocketOpen();
      this.terminal.reset();
    });

    this.ws.addEventListener("message", (event) => {
      this.terminal.write(event.data);
    });

    this.ws.addEventListener("close", (event) => {
      this.props.onWebSocketClose && this.props.onWebSocketClose();
      console.log("websocket close", event);

      const { code } = event;
      if (code !== 4000) {
        this.terminal.writeln("\nconnection closed");
      }
    });
  }

  private messageWebSocket(value: string) {
    this.ws &&
      this.ws.send(JSON.stringify({ type: "message", message: value }));
  }

  closeWebSocket() {
    this.ws &&
      this.ws.send(JSON.stringify({ type: "signal", message: "SIGINT" }));
  }

  killWebSocket() {
    this.ws &&
      this.ws.send(JSON.stringify({ type: "signal", message: "SIGKILL" }));
  }

  render() {
    return (
      <div style={{ height: "100%", width: "100%" }} ref={this.elementRef} />
    );
  }
}

export default Terminal;
