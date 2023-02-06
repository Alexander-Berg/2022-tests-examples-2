
import { Locator } from "playwright-core";
import { BaseComponent, Collection, ButtonElement } from "../../../../../../lib";

export class TutorialFragment extends BaseComponent {
    stepsLstReact: Collection<ButtonElement>;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, 'Report tutorial');
        this.stepsLstReact = new Collection(this.locator.locator('.sc-cNnxps.cdXYEZ'), this, ButtonElement, 'Navigation');
    }
}
