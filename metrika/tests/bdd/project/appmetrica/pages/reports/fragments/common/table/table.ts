
import { Locator } from "playwright-core";
import {BaseComponent} from "../../../../../../../lib";
import {TableHeadFragment} from "./tableHead";
import {TableBodyComponent} from "./tableBody";

export class TableComponent extends BaseComponent {
    tableHead: TableHeadFragment;
    tableBody: TableBodyComponent;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Table");
        this.tableHead = new TableHeadFragment(
            this.locator.locator(".sc-uJMKN.jsQhVl"),
            this
        );
        this.tableBody = new TableBodyComponent(
            this.locator.locator(".sc-bbmXgH.fNYDXK"),
            this
        );
    }
}
