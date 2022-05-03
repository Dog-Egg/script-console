import React from "react";

export const UserContext = React.createContext<{
  id: any;
  isAdmin: boolean;
  anonymous: boolean;
}>({
  id: undefined,
  anonymous: true,
  isAdmin: false,
});
