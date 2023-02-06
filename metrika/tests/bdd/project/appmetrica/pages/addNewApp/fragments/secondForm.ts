import { Locator } from "playwright-core";
import {
    BaseComponent, ButtonElement, InputElement
} from "../../../../../lib";

export class SecondFormComponent extends BaseComponent {

    popupGDPRButton: ButtonElement;
    popupTimezoneButton: ButtonElement;
    inputEmail: InputElement;
    buttonAddApp: ButtonElement;

    constructor(locator: Locator, parent: any, name: string) {
        super(locator, parent, name);

        this.popupTimezoneButton = new ButtonElement(
            this.locator.locator(".control.button2.button2_view_classic").nth(0),
            this,
            "select store button"
        );

        this.popupGDPRButton = new ButtonElement(
            this.locator.locator(".control.button2.button2_view_classic").nth(1),
            this,
            "show additional gdpr agreement"
        );

        this.buttonAddApp = new ButtonElement(
            this.locator.locator(".button2_theme_action"),
            this,
            "Add app button"
        );

        this.inputEmail = new InputElement(
            this.locator.locator("[name='email']"),
            this,
            "input e-mail field"
        );

    }
}
