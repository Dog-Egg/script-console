import "./style.scss";
import React, { useEffect, useState } from "react";
import { Terminal } from "xterm";
import "xterm/css/xterm.css";
import { FitAddon } from "xterm-addon-fit";
import { SearchAddon } from "xterm-addon-search";
import { WebLinksAddon } from "xterm-addon-web-links";
import { Input } from "antd";
import { DownOutlined, SearchOutlined, UpOutlined } from "@ant-design/icons";
import Icon from "@ant-design/icons";
import { ReactComponent as StopSvg } from "../../icons/suspend.svg";
import { ReactComponent as RunSvg } from "../../icons/execute.svg";
import { ReactComponent as ReRunSvg } from "../../icons/reRun.svg";
import { ReactComponent as KillSvg } from "../../icons/killProcess.svg";
import classNames from "classnames";

import figlet from "figlet";
import standard from "figlet/importable-fonts/Standard.js";
import Directory from "../Directory";

figlet.parseFont("Standard", standard);

let term;
let socket;
let searchAddon;

export default function Workbench() {
  // xterm
  useEffect(() => {
    term = new Terminal({
      cursorBlink: true,
      tabStopWidth: 4,
      convertEol: true,
      theme: {
        selection: "rgb(252,229,70)",
      },
    });

    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.open(document.getElementById("terminal"));
    fitAddon.fit();

    searchAddon = new SearchAddon();
    term.loadAddon(searchAddon);

    term.loadAddon(new WebLinksAddon());

    term.onData((data) => {
      if (socket) {
        socket.send(JSON.stringify({ type: "message", message: data }));
      }
    });

    figlet("Script Console", function (err, data) {
      term.writeln(data);
      term.writeln(`\x1b[1;3;33m${"\n 请点击侧边栏执行脚本"}\x1B[0m`);
    });

    function onResize() {
      fitAddon.fit();
    }

    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
    };
  }, []);

  const [currentScript, setCurrentScript] = useState();

  function runScript(path) {
    // clear
    if (socket) {
      socket.close(4000);
    }
    term.clear();

    socket = new WebSocket(
      `ws://${window.location.host}/socket/run?script=${path}`
    );
    socket.addEventListener("open", function () {
      setState(STATES.RUNNING);
    });

    socket.addEventListener("message", function (event) {
      term.write(event.data);
    });

    socket.addEventListener("close", function ({ code }) {
      setState(STATES.STOPPED);
      if (code === 4000) {
        term.reset();
      } else {
        term.writeln(`\nconnection closed`);
      }
    });
  }

  // 搜索
  const [search, setSearch] = useState("");
  useEffect(() => {
    term.clearSelection();
    if (search) {
      searchAddon.findNext(search);
    }
  }, [search]);

  // 脚本运行状态
  const STATES = {
    RUNNING: 0,
    STOPPED: 1,
    STOP: 2,
  };
  const [state, setState] = useState(STATES.STOPPED);
  const isStopped = state === STATES.STOPPED;
  const isRunnable = isStopped && currentScript;
  const isRunning = state === STATES.RUNNING;

  return (
    <div className="workbench">
      <aside>
        <Directory
          onClickScript={(path) => {
            setCurrentScript(path);
            runScript(path);
          }}
        />
      </aside>
      <main>
        <div className="toolbar">
          <div className="operations">
            {isStopped ? (
              <Icon
                component={RunSvg}
                className={classNames([
                  "op",
                  "op-green",
                  !isRunnable && "op-disabled",
                ])}
                onClick={() => {
                  if (isRunnable) {
                    runScript(currentScript);
                  }
                }}
              />
            ) : (
              <Icon
                component={ReRunSvg}
                className={classNames(["op", "op-green"])}
                onClick={() => {
                  if (isRunning) {
                    runScript(currentScript);
                  }
                }}
              />
            )}

            {state !== STATES.STOP ? (
              <Icon
                component={StopSvg}
                className={classNames([
                  "op",
                  "op-red",
                  !isRunning && "op-disabled",
                ])}
                onClick={() => {
                  if (isRunning) {
                    setState(STATES.STOP);
                    socket.send(
                      JSON.stringify({ type: "signal", message: "SIGINT" })
                    );
                  }
                }}
              />
            ) : (
              <Icon
                component={KillSvg}
                className={classNames(["op", "op-red"])}
                onClick={() => {
                  socket.send(
                    JSON.stringify({ type: "signal", message: "SIGKILL" })
                  );
                }}
              />
            )}
          </div>
          <div className="search">
            <Input
              allowClear
              size="small"
              style={{ width: 250 }}
              placeholder="搜索"
              prefix={<SearchOutlined />}
              addonAfter={
                <>
                  <UpOutlined
                    onClick={() => {
                      searchAddon.findPrevious(search);
                    }}
                  />
                  <DownOutlined
                    onClick={() => {
                      searchAddon.findNext(search);
                    }}
                  />
                </>
              }
              onInput={(e) => {
                setSearch(e.target.value);
              }}
            />
          </div>
        </div>
        <div id="terminal" />
      </main>
    </div>
  );
}
