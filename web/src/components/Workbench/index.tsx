import "./style.scss";
import React, { useEffect, useRef, useState } from "react";
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
import Terminal from "../Terminal";
import Resizable from "../Resizable";

figlet.parseFont("Standard", standard);

export default function Workbench() {
  const terminalRef = useRef<Terminal>(null);
  // xterm
  useEffect(() => {
    figlet("Script Console", function (err, data) {
      if (terminalRef.current && data) {
        terminalRef.current.writeln(data);
        terminalRef.current.writeln(
          `\x1b[1;3;33m\n 请"右键"单击侧边栏文件，然后"运行"脚本\x1B[0m`
        );
      }
    });
  }, []);

  const [currentScript, setCurrentScript] = useState<string>();

  function runScript(path: string) {
    terminalRef.current &&
      terminalRef.current.openWebSocket(
        `ws://${window.location.host}/ws/run?script=${path}`
      );
  }

  // 搜索
  const [search, setSearch] = useState<string>("");
  useEffect(() => {
    if (!terminalRef.current) return;

    terminalRef.current.clearSelection();
    if (search) {
      terminalRef.current.searchNext(search);
    }
  }, [search]);

  // 脚本运行状态
  enum StateEnum {
    RUNNING,
    STOPPED,
    STOP,
  }
  const [state, setState] = useState(StateEnum.STOPPED);
  const isStopped = state === StateEnum.STOPPED;
  const isRunnable = isStopped && currentScript;
  const isRunning = state === StateEnum.RUNNING;

  return (
    <div className="workbench">
      <aside>
        <Resizable resizeHandleAxis={"e"} width={300} height={"100%"}>
          <Directory
            onRunScript={(path: string) => {
              setCurrentScript(path);
              runScript(path);
            }}
          />
        </Resizable>
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
                  if (isRunning && currentScript) {
                    runScript(currentScript);
                  }
                }}
              />
            )}

            {state !== StateEnum.STOP ? (
              <Icon
                component={StopSvg}
                className={classNames([
                  "op",
                  "op-red",
                  !isRunning && "op-disabled",
                ])}
                onClick={() => {
                  if (isRunning) {
                    setState(StateEnum.STOP);
                    terminalRef.current && terminalRef.current.closeWebSocket();
                  }
                }}
              />
            ) : (
              <Icon
                component={KillSvg}
                className={classNames(["op", "op-red"])}
                onClick={() => {
                  terminalRef.current && terminalRef.current.killWebSocket();
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
                      terminalRef.current &&
                        terminalRef.current.searchPrevious(search);
                    }}
                  />
                  <DownOutlined
                    onClick={() => {
                      terminalRef.current &&
                        terminalRef.current.searchNext(search);
                    }}
                  />
                </>
              }
              onInput={(e: any) => {
                setSearch(e.target.value);
              }}
            />
          </div>
        </div>
        <Terminal
          ref={terminalRef}
          onWebSocketOpen={() => setState(StateEnum.RUNNING)}
          onWebSocketClose={() => setState(StateEnum.STOPPED)}
        />
      </main>
    </div>
  );
}
