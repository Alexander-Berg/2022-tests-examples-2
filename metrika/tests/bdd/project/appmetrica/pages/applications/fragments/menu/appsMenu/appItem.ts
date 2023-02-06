import { Locator } from "playwright-core";
import {
    BaseComponent,
    ButtonElement,
    TextElement,
} from "../../../../../../../lib";

export class AppItemComponent extends BaseComponent {
    changeFolder: ButtonElement;
    title: TextElement;
    settingButton: ButtonElement;
    constructor(locator: Locator, parent: any, name: string) {
        super(locator, parent, name);
        this.title = new TextElement(
            this.locator.locator(".menu-apps-item__link"),
            this,
            name
        );
        this.changeFolder = new ButtonElement(
            this.locator.locator(".icon__arrow-small.menu-apps-item__options-change-folder"),
            this,
            name
        );
        this.settingButton = new ButtonElement(
            this.locator.locator(".icon__app-settings.menu-apps-item__settings"),
            this,
            name
        );
    }
}
