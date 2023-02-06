
import { Locator } from "playwright-core";
import {BaseComponent, Collection} from "../../../../../../../lib";
import {ButtonReportElement} from "../../../elements";

export class TableAdapterControlsAudienceFragment extends BaseComponent {
    dimensionsList: Collection<ButtonReportElement>;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Chart header");
        this.dimensionsList = new Collection(
            this.locator.locator(".radio-button__radio.table-grouping-switcher__radio"),
            this,
            ButtonReportElement,
            "Available dimensions"
        );
    }
}
