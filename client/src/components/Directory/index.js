import { Tree, Dropdown, Menu, Modal } from "antd";
import React, { useEffect, useRef, useState } from "react";
import {
  downloadFile,
  getDirectoryTree,
  readFile,
  makeDir,
  makeFile,
  removeFile,
  renameFile,
  writeFile,
  uploadFile,
} from "../../api";
import {
  CaretRightOutlined,
  DeleteOutlined,
  DownloadOutlined,
  EditOutlined,
  FileAddOutlined,
  FileOutlined,
  FileProtectOutlined,
  FileSyncOutlined,
  FolderAddOutlined,
  FolderOpenOutlined,
  FolderOutlined,
  UploadOutlined,
} from "@ant-design/icons";
import prompt from "../Prompt";
import * as nodePath from "path";
import CodeEditor from "../CodeEditor";
import { Steps as IntroSteps } from "intro.js-react";
import "intro.js/introjs.css";
import "./style.scss";
import { useCurrentUser } from "../../utils/hooks";

const { DirectoryTree } = Tree;

export default function Directory({ onRunScript, onSelect }) {
  const currentUser = useCurrentUser();
  const [treeData, setTreeData] = useState([]);
  const [selectedKeys, setSelectedKeys] = useState([]);
  const [selectedNode, setSelectedNode] = useState();

  function updateDirectory() {
    getDirectoryTree().then((resp) => {
      setSelectedNode();
      const data = resp.data.data;
      if (!localStorage.getItem("intro")) {
        data.push({ title: "演示文件.js", key: Date.now(), isLeaf: true });
        setTimeout(() => {
          setIntroEnable(true);
        });
      }
      setTreeData(data);
    });
  }

  useEffect(() => {
    updateDirectory();
  }, []);

  // anchor
  useEffect(() => {
    const anchor = window.location.hash.substring(1);
    if (anchor) {
      setSelectedKeys([decodeURI(anchor)]);
    }
  }, []);
  useEffect(() => {
    if (selectedKeys.length) {
      window.history.replaceState("", "", `#${selectedKeys[0]}`);
    }
  }, [selectedKeys]);

  const directoryTree = Boolean(treeData.length) && (
    <DirectoryTree
      defaultExpandedKeys={[selectedKeys]}
      icon={function (node) {
        if (node.isLeaf) {
          if (node["isSys"]) {
            return <FileProtectOutlined />;
          }
          return <FileOutlined />;
        } else {
          if (node.expanded) {
            return <FolderOpenOutlined />;
          }
          return <FolderOutlined />;
        }
      }}
      selectedKeys={selectedKeys}
      treeData={treeData}
      onSelect={function (keys, { node }) {
        onSelect && onSelect(...arguments);
        setSelectedKeys(keys);
        setSelectedNode(node);
      }}
      onRightClick={function ({ node }) {
        setSelectedNode(node);
        setSelectedKeys([node.key]);
      }}
    />
  );

  function pathJoin(path) {
    if (!selectedNode) {
      return path;
    }

    const parent = selectedNode["key"];
    if (selectedNode["isLeaf"]) {
      return nodePath.join(nodePath.dirname(parent), path);
    }
    return nodePath.join(parent, path);
  }

  const [editingFile, setEditingFile] = useState({});

  function getDropdownMenu() {
    const operations = {
      MAKE_FILE: "1",
      MAKE_DIR: "2",
      REMOVE: "3",
      EDIT_FILE: "4",
      RENAME: "5",
      UPLOAD: "6",
      DOWNLOAD: "7",
      RUN: "8",
    };

    const userIsAdmin = currentUser.isAdmin;
    const nodeIsFile = selectedNode && selectedNode["isLeaf"];
    const fileIsSys = selectedNode && selectedNode["isSys"];

    return (
      <Menu
        onClick={({ key }) => {
          switch (key) {
            case operations.MAKE_FILE:
              prompt({ title: "创建文件" }).then((value) => {
                makeFile(pathJoin(value)).then(updateDirectory);
              });
              break;
            case operations.MAKE_DIR:
              prompt({ title: "创建目录" }).then((value) => {
                makeDir(pathJoin(value)).then(updateDirectory);
              });
              break;
            case operations.REMOVE:
              Modal.confirm({
                title: `确认删除 ${selectedNode["key"]}?`,
                onOk() {
                  removeFile(selectedNode["key"]).then(updateDirectory);
                },
              });
              break;
            case operations.RENAME:
              prompt({
                title: "重命名",
                defaultValue: selectedNode["title"],
              }).then((value) => {
                renameFile(
                  selectedNode["key"],
                  nodePath.join(nodePath.dirname(selectedNode["key"]), value)
                ).then(updateDirectory);
              });
              break;
            case operations.EDIT_FILE:
              readFile(selectedNode["key"]).then((resp) => {
                setEditingFile(resp.data);
                setEditorVisible(true);
              });
              break;
            case operations.RUN:
              onRunScript && onRunScript(selectedNode["key"]);
              break;
            case operations.UPLOAD:
              uploadRef.current.click();
              break;
            case operations.DOWNLOAD:
              downloadFile(selectedNode["key"]);
              break;
            default:
          }
        }}
      >
        {nodeIsFile && (
          <>
            <Menu.Item
              key={operations.RUN}
              icon={<CaretRightOutlined />}
              disabled={fileIsSys}
            >
              运行
            </Menu.Item>
            <Menu.Item
              key={operations.EDIT_FILE}
              icon={<EditOutlined />}
              disabled={!userIsAdmin}
            >
              编辑
            </Menu.Item>
            <Menu.Divider />
          </>
        )}
        <Menu.Item
          key={operations.MAKE_FILE}
          icon={<FileAddOutlined />}
          disabled={!userIsAdmin}
        >
          创建文件
        </Menu.Item>
        <Menu.Item
          key={operations.MAKE_DIR}
          icon={<FolderAddOutlined />}
          disabled={!userIsAdmin}
        >
          创建目录
        </Menu.Item>
        <Menu.Divider />
        <Menu.Item
          key={operations.UPLOAD}
          icon={<UploadOutlined />}
          disabled={!userIsAdmin}
        >
          上传文件
        </Menu.Item>
        {nodeIsFile && (
          <Menu.Item
            key={operations.DOWNLOAD}
            icon={<DownloadOutlined />}
            disabled={!userIsAdmin}
          >
            下载文件
          </Menu.Item>
        )}
        {selectedNode && (
          <>
            <Menu.Divider />
            <Menu.Item
              key={operations.RENAME}
              icon={<FileSyncOutlined />}
              disabled={fileIsSys || !userIsAdmin}
            >
              重命名
            </Menu.Item>
          </>
        )}
        {selectedNode && (
          <>
            <Menu.Divider />
            <Menu.Item
              key={operations.REMOVE}
              icon={<DeleteOutlined />}
              disabled={fileIsSys || !userIsAdmin}
            >
              删除
            </Menu.Item>
          </>
        )}
      </Menu>
    );
  }

  const [editorVisible, setEditorVisible] = useState(false);

  const uploadRef = useRef();

  function handleUpload(event) {
    const file = event.target.files[0];
    event.target.value = "";
    uploadFile(file, pathJoin("/")).then(updateDirectory);
  }

  const [introEnable, setIntroEnable] = useState(false);
  return (
    <>
      <IntroSteps
        enabled={introEnable}
        initialStep={0}
        steps={[
          {
            element: ".ant-tree-treenode:last-child",
            intro: <span>"右键"单击文件，然后"运行"脚本</span>,
            title: "运行脚本",
          },
        ]}
        onExit={() => {
          setIntroEnable(false);
          const data = [...treeData];
          data.pop();
          setTreeData(data);
          localStorage.setItem("intro", "true");
        }}
        options={{
          showBullets: false,
          showButtons: false,
          exitOnOverlayClick: false,
          highlightClass: "customHighlight",
          tooltipPosition: "right",
        }}
      />
      <Dropdown overlay={getDropdownMenu} trigger={["contextMenu"]}>
        <div style={{ height: "100%", overflow: "auto" }}>{directoryTree}</div>
      </Dropdown>
      <CodeEditor
        visible={editorVisible}
        title={editingFile["path"]}
        content={editingFile.content}
        onCancel={() => setEditorVisible(false)}
        onOk={(content) => {
          writeFile(editingFile.path, content).then(() => {
            setEditorVisible(false);
          });
        }}
      />
      <input
        style={{ display: "none" }}
        ref={uploadRef}
        type="file"
        onChange={handleUpload}
      />
    </>
  );
}
