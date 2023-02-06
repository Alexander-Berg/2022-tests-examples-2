import {nested} from "./nested-dep.view.js";

function sub() {
    console.log("SERVER:imported-dep");
}

export function clientside() {
    console.log("SERVER:client-imported");
    sub();
}

export function serverside() {
    console.log("SERVER:not-imported");
    nested();
}
