
import { Locator } from "playwright-core";
import {BaseComponent, Collection} from "../../../../../../lib";
import {ButtonReportElement} from "../../elements";

export class ReportControlsFragment extends BaseComponent {
    controlsBar: Collection<ButtonReportElement>;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Report controls bar");

        this.controlsBar = new Collection(
            this.locator.locator(".ControlsBar__item"),
            this,
            ButtonReportElement,
            "Controls bar buttons"
        );
    }
}
