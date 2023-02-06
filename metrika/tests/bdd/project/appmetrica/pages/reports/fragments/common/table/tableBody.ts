
import { Locator } from "playwright-core";
import {BaseComponent, Collection} from "../../../../../../../lib";
import {RowComponent} from "./row";

export class TableBodyComponent extends BaseComponent {
    rowsList: Collection<RowComponent>;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Table body");

        this.rowsList = new Collection<RowComponent>(
            this.locator.locator(".sc-jqCOkK.dUAbGW"),
            this,
            RowComponent,
            "Collection of rows"
        );
    }
}
