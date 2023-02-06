import { Locator } from "playwright-core";
import { AppItemComponent } from ".";
import {
    BaseComponent,
    Collection,
    ButtonElement,
} from "../../../../../../../lib";

export class AppsListFragment extends BaseComponent {
    appButton: ButtonElement;
    appsList: Collection<AppItemComponent>;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Apps list in menu");

        this.appButton = new ButtonElement(
            this.locator.locator(".menu-apps-item"),
            this,
            "App button"
        );
        this.appsList = new Collection(
            this.locator.locator(".menu-apps-item"),
            this,
            AppItemComponent,
            "Applications"
        );
    }

    async getAppNames() {
        const appNames = (await this.locator
            .locator(".menu-apps-item__link")
            .allInnerTexts());
        for (let i = 0; i < appNames.length; i++) {
            appNames[i] = appNames[i].replace(/\n\W*/,'');
        }
        return appNames;
    }
}
