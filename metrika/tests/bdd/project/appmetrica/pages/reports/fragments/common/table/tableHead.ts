import { Locator } from "playwright-core";
import {BaseComponent, Collection} from "../../../../../../../lib";
import {RowComponent} from "./row";
import {ButtonReportElement} from "../../../elements";

export class TableHeadFragment extends BaseComponent {
    sortMetricButtons: Collection<ButtonReportElement>;
    summaryRow: RowComponent;
    breadcrumbs: Collection<ButtonReportElement>;

    constructor(locator: Locator, parent: any){
        super(locator, parent, "Table head");

        this.breadcrumbs = new Collection<ButtonReportElement>(
            this.locator.locator(".sc-bRBYWo.hFxdh"),
            this,
            ButtonReportElement,
            "Groupings breadcrumbs"
        );
        this.sortMetricButtons = new Collection<ButtonReportElement>(
            this.locator.locator(".sc-cJSrbW.sc-hmzhuo.sc-frDJqD .sc-jDwBTQ.BbJXr"),
            this,
            ButtonReportElement,
            "Sort asc/desc buttons list"
        );
        this.summaryRow = new RowComponent(
            this.locator.locator(".sc-dNLxif.hPKYxF"),
            this
        );
    }
    async getColumnMetricNames(){
        await this.sortMetricButtons.clear();
        const metricList = await this.sortMetricButtons.init();
        const columnNames = [];
        for (let i = 0; i < metricList.size(); i++) {
            columnNames.push(await metricList.get(i).getText());
        }
        return columnNames;
    }
}
