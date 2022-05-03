import { useContext } from "react";
import { UserContext } from "./ctx";

export function useCurrentUser() {
  return useContext(UserContext);
}
