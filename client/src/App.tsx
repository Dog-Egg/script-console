import "./App.scss";
import React, { useState } from "react";
import Console from "./components/Console";
import Menu from "./components/Menu";
import Workbench from "./components/Workbench";
import Users from "./components/Users";
import Split from "./components/Split";
import Config from "./components/Config";

function App() {
  const [currentMenu, setCurrentMenu] = useState(Menu.itemNames.WORKBENCH);
  const [enableConsole, setEnabledConsole] = useState(false);

  const onClickMenuItem = (name: string, selected: () => void) => {
    switch (name) {
      case Menu.itemNames.WORKBENCH:
      case Menu.itemNames.USERS:
      case Menu.itemNames.CONFIG:
        setCurrentMenu(name);
        selected();
        break;
      case Menu.itemNames.CONSOLE:
        setEnabledConsole(true);
        break;
    }
  };

  return (
    <div className="layout">
      <div className="layout-menu">
        <Menu defaultItemName={currentMenu} onClickMenuItem={onClickMenuItem} />
      </div>
      <Split
        className="layout-main"
        sizes={enableConsole ? [70, 30] : undefined}
        direction="vertical"
      >
        <div className="layout-main-part1">
          {currentMenu === Menu.itemNames.WORKBENCH && <Workbench />}
          {currentMenu === Menu.itemNames.USERS && <Users />}
          {currentMenu === Menu.itemNames.CONFIG && <Config />}
        </div>
        {enableConsole && (
          <div className="layout-main-part2">
            <Console onClose={() => setEnabledConsole(false)} />
          </div>
        )}
      </Split>
    </div>
  );
}

export default App;
