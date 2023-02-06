
import { Locator } from "playwright-core";
import {BaseComponent, TextElement} from "../../../../../../../lib";
import {ButtonReportElement} from "../../../elements";

export class DimensionCellAudienceFragment extends BaseComponent {
    checkbox: ButtonReportElement;
    dimensionCellNonClickable: TextElement;
    dimensionCellClickable: ButtonReportElement;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Table row");

        this.checkbox = new ButtonReportElement(
            this.locator.locator(".checkbox"),
            this,
            "Checkbox"
        );
        this.dimensionCellNonClickable = new TextElement(
            this.locator
                .locator(".statistic-table-adapter__dimension-title-cell"),
            this,
            "Dimension cell non-clickable"
        );
        this.dimensionCellClickable = new ButtonReportElement(
            this.locator.locator(".statistic-table-adapter__next-level"),
            this,
            "Dimension cell clickable"
        );
    }
}
