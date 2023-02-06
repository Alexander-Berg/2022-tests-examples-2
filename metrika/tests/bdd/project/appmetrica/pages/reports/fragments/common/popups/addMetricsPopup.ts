
import { Locator } from "playwright-core";
import {BaseComponent, ButtonElement, Collection, InputElement} from "../../../../../../../lib";
import {ButtonReportElement} from "../../../elements";

export class AddMetricsPopupFragment extends BaseComponent {
    metricsList: Collection<ButtonReportElement>;
    searchField: InputElement;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Metrics selector");
        this.metricsList = new Collection(
            this.locator.locator(".sc-jKJlTe.jOHEWl div .sc-ckVGcZ.eJMTvT"),
            this,
            ButtonReportElement,
            "List of metrics to select"
        );
        this.searchField = new InputElement(
            this.locator.locator(".textinput__control"),
            this,
            "Search field"
        );
    }

    async openAllGroups() {
        const groups = await (new Collection<ButtonElement>(
            this.locator.locator(".sc-dxgOiQ.gIfLjq"),
            this,
            ButtonElement,
            "Metrics parents list"
        )).init();
        for (let i = 0; i < groups.size(); i++) {
            await (groups.get(i)).click();
        }
    }
}

