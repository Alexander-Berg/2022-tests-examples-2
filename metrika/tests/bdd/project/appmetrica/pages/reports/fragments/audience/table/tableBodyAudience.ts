
import { Locator } from "playwright-core";
import {BaseComponent, Collection} from "../../../../../../../lib";
import {RowAudienceComponent} from "./rowAudience";

export class TableBodyAudienceComponent extends BaseComponent {
    summaryRow: Collection<RowAudienceComponent>;
    rowsList: Collection<RowAudienceComponent>;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Table body");
        this.summaryRow = new Collection<RowAudienceComponent>(
            this.locator.locator(".simple-data-table__row_summary"),
            this,
            RowAudienceComponent,
            "Summary row"
        );
        this.rowsList = new Collection<RowAudienceComponent>(
            this.locator.locator(".simple-data-table__row.complex-data-table__row:not(:first-child)"),
            this,
            RowAudienceComponent,
            "Collection of rows"
        );
    }
}
