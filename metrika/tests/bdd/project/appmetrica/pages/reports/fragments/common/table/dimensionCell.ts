
import { Locator } from "playwright-core";
import {BaseComponent, TextElement} from "../../../../../../../lib";
import {ButtonReportElement} from "../../../elements";

export class DimensionCellFragment extends BaseComponent {
    checkbox: ButtonReportElement;
    dimensionCellListView: ButtonReportElement;
    dimensionCellDrillDown: TextElement;
    drilldownPlus: ButtonReportElement;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Table row");

        this.checkbox = new ButtonReportElement(
            this.locator.locator(".sc-cHGsZl.PGyIQ"),
            this,
            "Checkbox"
        );
        this.dimensionCellListView = new ButtonReportElement(
            this.locator.locator(".sc-ccbnFN.eFRbGm [role='button']"),
            this,
            "Dimension cell"
        );
        this.dimensionCellDrillDown = new TextElement(
            this.locator.locator(".sc-ccbnFN.eFRbGm span"),
            this,
            "Dimension cell"
        );
        this.drilldownPlus = new ButtonReportElement(
            this.locator.locator(".sc-kjoXOD.akCKc"),
            this,
            "Expand/reduce tree button"
        );
    }
}
