
import { Locator } from "playwright-core";
import {BaseComponent, Collection} from "../../../../../../lib";
import {ButtonReportElement} from "../../elements";

export class ChartHeaderFragment extends BaseComponent {
    chartChanger: Collection<ButtonReportElement>;
    metricPicker: ButtonReportElement;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Chart header");

        this.metricPicker = new ButtonReportElement(
            this.locator.locator("[type='button']"),
            this,
            "Metric picker for chart"
        );
        this.chartChanger = new Collection(
            this.locator.locator(".sc-cBOTKl"),
            this,
            ButtonReportElement,
            "Available charts"
        );
    }
}
