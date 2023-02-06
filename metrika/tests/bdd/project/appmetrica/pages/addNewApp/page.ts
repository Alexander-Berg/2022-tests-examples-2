import { Page } from "playwright-core";
import {BaseComponent, BasePage} from "../../../../lib";
import {
    AddNewAppFragment,
    DropDownFragment
} from "./fragments";

export class AddNewAppPage extends BasePage {
    addNewAppFragment: AddNewAppFragment;
    popupAppCategoryFragment: DropDownFragment;
    popupStoreCategoryFirstFragment: DropDownFragment;
    popupStoreCategorySecondFragment: DropDownFragment;
    popupTimezoneFragment: DropDownFragment;
    popupGDPRFragment: BaseComponent;

    constructor(page: Page) {
        super(page, "Create new app", "/application/new");
        this.addNewAppFragment = new AddNewAppFragment(
            this.page.locator(".page-app-create"),
            this
        );
        this.popupAppCategoryFragment = new DropDownFragment(
            this.page.locator(".popup2_view_classic.popup2_tone_default.popup2_theme_normal").nth(0),
            this,
            "App category"
        );
        this.popupStoreCategoryFirstFragment = new DropDownFragment(
            this.page.locator(".popup2_view_classic.popup2_tone_default.popup2_theme_normal").nth(2),
            this,
            "First App store provider"
        );
        this.popupStoreCategorySecondFragment = new DropDownFragment(
            this.page.locator(".popup2_view_classic.popup2_tone_default.popup2_theme_normal").nth(3),
            this,
            "Second App store provider"
        );
        this.popupTimezoneFragment = new DropDownFragment(
            this.page.locator(".popup2_view_classic.popup2_tone_default.popup2_theme_normal").last(),
            this,
            "Timezone"
        );

        this.popupGDPRFragment = new BaseComponent(
            this.page.locator(".sc-fOKMvo.gIpTE"),
            this,
            "GDPR popup fragment"
        );


    }
}

export function getAddNewAppPage(page: Page) {
    return new AddNewAppPage(page);
}
