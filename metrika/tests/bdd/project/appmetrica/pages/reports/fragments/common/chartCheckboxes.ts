
import { Locator } from "playwright-core";
import {BaseComponent, Collection} from "../../../../../../lib";
import {ButtonReportElement} from "../../elements";

export class ChartCheckboxesFragment extends BaseComponent {
    checkboxesList: Collection<ButtonReportElement>;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Chart checkboxes");
        this.checkboxesList = new Collection(
            this.locator.locator("[type='checkbox']"),
            this,
            ButtonReportElement,
            "Available chart checkboxes"
        );
    }
}
