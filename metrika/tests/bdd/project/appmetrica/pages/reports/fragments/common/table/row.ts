
import { Locator } from "playwright-core";
import {BaseComponent, Collection, TextElement} from "../../../../../../../lib";
import {DimensionCellFragment} from "./dimensionCell";

export class RowComponent extends BaseComponent {
    metricCells: Collection<TextElement>;
    dimensionCellFragment: DimensionCellFragment;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Table row");
        this.metricCells = new Collection<TextElement>(
            this.locator.locator(".sc-cJSrbW.sc-hmzhuo.YROvH"),
            this,
            TextElement,
            "Metric cells"
        );
        this.dimensionCellFragment = new DimensionCellFragment(
            this.locator.locator(".sc-cJSrbW.sc-kvZOFW"),
            this
        );
    }
}
