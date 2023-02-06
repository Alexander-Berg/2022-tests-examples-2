
import { Locator } from "playwright-core";
import {BaseComponent, Collection, TextElement} from "../../../../../../../lib";
import {DimensionCellAudienceFragment} from "./dimensionCellAudience";

export class RowAudienceComponent extends BaseComponent {
    metricCells: Collection<TextElement>;
    dimensionCell: DimensionCellAudienceFragment;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Table row");
        this.metricCells = new Collection<TextElement>(
            this.locator.locator(".simple-data-table__cell_text_right"),
            this,
            TextElement,
            "Metric cells"
        );
        this.dimensionCell = new DimensionCellAudienceFragment(
            this.locator.locator(".simple-data-table__cell").first(),
            this
        );
    }
}
