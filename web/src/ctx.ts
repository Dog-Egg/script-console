import React from "react";

export const UserContext = React.createContext<UserInterface>({
  anonymous: true,
  isAdmin: false,
});
