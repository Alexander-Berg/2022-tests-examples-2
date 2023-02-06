import "./imported.client.js";
import {other} from "./next-imported.view.js";
import {lonely} from "./no-client.view.js";

export function onlyOne() {
    console.log("SERVER:imported");
    other();
    lonely();
}
