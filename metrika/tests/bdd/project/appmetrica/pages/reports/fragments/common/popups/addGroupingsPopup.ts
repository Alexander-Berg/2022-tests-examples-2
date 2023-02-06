
import { Locator } from "playwright-core";
import {BaseComponent, ButtonElement, Collection} from "../../../../../../../lib";

export class AddGropingsPopupFragment extends BaseComponent {
    groupingsList: Collection<ButtonElement>;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Groupings selector");
        this.groupingsList = new Collection(
            this.locator.locator(".sc-jKJlTe.jOHEWl div .sc-ckVGcZ.eJMTvT"),
            this,
            ButtonElement,
            "List of groupings to select"
        );
    }

    async openAllGroups() {
        const groups = await (new Collection<ButtonElement>(
            this.locator.locator(".sc-dxgOiQ.gIfLjq"),
            this,
            ButtonElement,
            "Groupings parents list"
        )).init();
        for (let i = 0; i < groups.size(); i++) {
            await (groups.get(i)).click();
        }
    }
}

