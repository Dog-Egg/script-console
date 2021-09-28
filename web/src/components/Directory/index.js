import { Tree, message, Dropdown, Menu, Modal } from "antd";
import React, { useContext, useEffect, useState } from "react";
import {
  getDirectory,
  getFile,
  makeFile,
  removeFile,
  updateFile,
} from "../../api";
import {
  DeleteOutlined,
  EditOutlined,
  FileAddOutlined,
  FileOutlined,
  FileProtectOutlined,
  FileSyncOutlined,
  FolderAddOutlined,
  FolderOpenOutlined,
  FolderOutlined,
} from "@ant-design/icons";
import prompt from "../Prompt";
import * as nodePath from "path";
import { UserContext } from "../../ctx";
import CodeEditor from "../CodeEditor";

const { DirectoryTree } = Tree;

export default function Directory({ onClickScript }) {
  const currentUser = useContext(UserContext);
  const [treeData, setTreeData] = useState();
  const [selectedKeys, setSelectedKeys] = useState([]);
  const [selectedNode, setSelectedNode] = useState();

  function updateDirectory() {
    getDirectory().then((resp) => {
      setTreeData(resp.data.directory);
    });
  }
  useEffect(() => {
    updateDirectory();
  }, []);

  const directoryTree = (
    <DirectoryTree
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
        if (node["isSys"]) {
          message.warning("系统文件，不可执行").then();
        } else {
          if (onClickScript && node.isLeaf) {
            onClickScript(keys[0]);
          }
        }
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
    };

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
                makeFile(pathJoin(value), true).then(updateDirectory);
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
              prompt({ title: "重命名" }).then((value) => {
                updateFile(selectedNode["key"], {
                  name: nodePath.join(
                    nodePath.dirname(selectedNode["key"]),
                    value
                  ),
                }).then(updateDirectory);
              });
              break;
            case operations.EDIT_FILE:
              getFile(selectedNode["key"]).then((resp) => {
                setEditingFile(resp.data);
                setEditorVisible(true);
              });
              break;
            default:
          }
        }}
      >
        {selectedNode && selectedNode["isLeaf"] && (
          <>
            <Menu.Item key={operations.EDIT_FILE} icon={<EditOutlined />}>
              编辑文件
            </Menu.Item>
            <Menu.Divider />
          </>
        )}
        <Menu.Item key={operations.MAKE_FILE} icon={<FileAddOutlined />}>
          创建文件
        </Menu.Item>
        <Menu.Item key={operations.MAKE_DIR} icon={<FolderAddOutlined />}>
          创建目录
        </Menu.Item>
        {selectedNode && (
          <>
            <Menu.Divider />
            <Menu.Item
              key={operations.RENAME}
              icon={<FileSyncOutlined />}
              disabled={selectedNode["isSys"]}
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
              disabled={selectedNode["isSys"]}
            >
              删除
            </Menu.Item>
          </>
        )}
      </Menu>
    );
  }

  const [editorVisible, setEditorVisible] = useState(false);

  if (currentUser.isAdmin) {
    return (
      <>
        <Dropdown overlay={getDropdownMenu} trigger={["contextMenu"]}>
          <div style={{ height: "100%" }}>{directoryTree}</div>
        </Dropdown>
        <CodeEditor
          visible={editorVisible}
          title={editingFile["path"]}
          content={editingFile.content}
          mode={editingFile["filetype"]}
          onCancel={() => setEditorVisible(false)}
          onOk={(content) => {
            updateFile(editingFile.path, { content }).then(() => {
              setEditorVisible(false);
            });
          }}
        />
      </>
    );
  }
  return directoryTree;
}
