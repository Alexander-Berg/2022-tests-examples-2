
import { Locator } from "playwright-core";
import {BaseComponent, Collection} from "../../../../../../lib";
import {ButtonReportElement} from "../../elements";

export class ChartHeaderAudienceFragment extends BaseComponent {
    chartChanger: Collection<ButtonReportElement>;
    reloadReport: ButtonReportElement;
    exportReport: ButtonReportElement;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Chart header");
        this.chartChanger = new Collection(
            this.locator.locator("[name='chart-type']"),
            this,
            ButtonReportElement,
            "Available charts"
        );
        this.reloadReport = new ButtonReportElement(
            this.locator.locator(".refresh-report-control__refresh-trigger button"),
            this,
            "Reload report button"
        );
        this.exportReport = new ButtonReportElement(
            this.locator.locator(".dropdown2_switcher_link button"),
            this,
            "Export report button"
        );
    }

}
