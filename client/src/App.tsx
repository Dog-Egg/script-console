import "./App.scss";
import React, { useState } from "react";
import Console from "./components/Console";
import Menu from "./components/Menu";
import Workbench from "./components/Workbench";
import Users from "./components/Users";
import Split from "./components/Split";
import { SplitProps } from "react-split";

function App() {
  const [currentMenu, setCurrentMenu] = useState(Menu.itemNames.WORKBENCH);
  const [enableConsole, setEnabledConsole] = useState(false);

  const onClickMenuItem = (name: string, selected: () => void) => {
    switch (name) {
      case Menu.itemNames.WORKBENCH:
      case Menu.itemNames.USERS:
        setCurrentMenu(name);
        selected();
        break;
      case Menu.itemNames.CONSOLE:
        setEnabledConsole(true);
        break;
    }
  };

  const splitOptions: SplitProps = {
    direction: "vertical",
    sizes: enableConsole ? [70, 30] : [100, 0],
    minSize: enableConsole ? undefined : 0,
  };

  return (
    <div className="layout">
      <div className="layout-menu">
        <Menu defaultItemName={currentMenu} onClickMenuItem={onClickMenuItem} />
      </div>
      <Split className="layout-main" {...splitOptions}>
        <div className="layout-main-upper">
          {currentMenu === Menu.itemNames.WORKBENCH && <Workbench />}
          {currentMenu === Menu.itemNames.USERS && <Users />}
        </div>
        <div className="layout-main-lower">
          {enableConsole && (
            <Console onClose={() => setEnabledConsole(false)} />
          )}
        </div>
      </Split>
    </div>
  );
}

export default App;
