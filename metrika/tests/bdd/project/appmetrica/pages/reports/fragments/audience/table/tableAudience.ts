
import { Locator } from "playwright-core";
import {BaseComponent} from "../../../../../../../lib";
import {TableHeadAudienceFragment} from "./tableHeadAudience";
import {TableBodyAudienceComponent} from "./tableBodyAudience";

export class TableAudienceComponent extends BaseComponent {
    tableHead: TableHeadAudienceFragment;
    tableBody: TableBodyAudienceComponent;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Table");
        this.tableHead = new TableHeadAudienceFragment(
            this.locator.locator(".simple-data-table__thead"),
            this
        );
        this.tableBody = new TableBodyAudienceComponent(
            this.locator.locator(".simple-data-table__tbody"),
            this
        );
    }
}
