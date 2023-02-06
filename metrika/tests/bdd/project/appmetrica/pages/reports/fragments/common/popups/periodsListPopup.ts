
import { Locator } from "playwright-core";
import {BaseComponent, ButtonElement, Collection} from "../../../../../../../lib";

export class PeriodsListPopupFragment extends BaseComponent {
    periodsList: Collection<ButtonElement>;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "List of periods to choose");

        this.periodsList = new Collection(
            this.locator
                .locator("[role='option']"),
            this,
            ButtonElement,
            "List of periods"
        );
    }
}
