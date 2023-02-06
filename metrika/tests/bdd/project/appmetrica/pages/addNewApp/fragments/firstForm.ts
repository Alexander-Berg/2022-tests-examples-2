import { Locator } from "playwright-core";
import {
    BaseComponent, ButtonElement, InputElement
} from "../../../../../lib";

export class FirstFormComponent extends BaseComponent {

    inputAppName: InputElement;
    inputAppLinkFirst: InputElement;
    inputAppLinkSecond: InputElement;
    popupCategoryButton: ButtonElement;
    popupStoreButton1: ButtonElement;
    popupStoreButton2: ButtonElement;
    buttonDeleteStoreLinkFirst: ButtonElement;
    buttonDeleteStoreLinkSecond: ButtonElement;
    buttonAddMoreStoreLink: ButtonElement;
    buttonContinue: ButtonElement;

    constructor(locator: Locator, parent: any, name: string) {
        super(locator, parent, name);

        this.inputAppName = new InputElement(
            this.locator.locator("[name='appname']"),
            this,
            "input AppName"
        );

        this.inputAppLinkFirst = new InputElement(
            this.locator.locator("[name='links[0].link']"),
            this,
            "input link to app"
        );

        this.inputAppLinkSecond = new InputElement(
            this.locator.locator("[name='links[0].link']"),
            this,
            "input link to app"
        );

        this.popupCategoryButton = new ButtonElement(
            this.locator.locator("button.control.button2.select2__button").nth(0),
            this,
            "select category button"
        );

        this.popupStoreButton1 = new ButtonElement(
            this.locator.locator("button.control.button2.select2__button").nth(1),
            this,
            "select store button"
        );
        this.popupStoreButton2 = new ButtonElement(
            this.locator.locator("button.control.button2.select2__button").nth(2),
            this,
            "select store button 2"
        );

        this.buttonAddMoreStoreLink = new ButtonElement(
            this.locator.locator(".button2_theme_clear"),
            this,
            "add more app store links button"
        );

        this.buttonDeleteStoreLinkFirst = new ButtonElement(
            this.locator.locator(".sc-krvtoX.gvGLNU").nth(0),
            this,
            "delete first link button"
        );

        this.buttonDeleteStoreLinkSecond = new ButtonElement(
            this.locator.locator(".sc-krvtoX.gvGLNU").nth(1),
            this,
            "delete second link button"
        );

        this.buttonContinue = new ButtonElement(
            this.locator.locator(".button2_theme_action"),
            this,
            "continue button"
        );
    }
}
