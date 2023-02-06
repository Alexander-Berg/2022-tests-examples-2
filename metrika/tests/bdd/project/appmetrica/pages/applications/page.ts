import { Page } from "playwright-core";
import {BasePage, ButtonElement, Collection} from "../../../../lib";
import {
    AppsMenuFragment,
    ReportFragment,
    ReportMenuFragment,
} from "./fragments";

export class ApplicationPage extends BasePage {
    appsMenuFragment: AppsMenuFragment;
    reportFragment: ReportFragment;
    reportsMenuFragment: ReportMenuFragment;
    popupChangeFolderFragment: Collection<ButtonElement>;

    constructor(page: Page) {
        super(page, "Apps", "/application/list");
        this.appsMenuFragment = new AppsMenuFragment(
            this.page.locator(".menu-apps"),
            this
        );
        this.reportsMenuFragment = new ReportMenuFragment(
            this.page.locator(".menu-reports"),
            this
        );
        this.reportFragment = new ReportFragment(
            this.page.locator(".page-layout__wrapper"),
            this
        );
        this.popupChangeFolderFragment = new Collection(
            this.page.locator(".menu-apps__custom-select-item.custom-select__default-item"),
            this,
            ButtonElement,
            "list of folders to put app in"
        );
    }

    async gotoReport(appId: number) {
        await this.goto(`${global.baseAppmetricaUrl}/statistic?appId=${appId}`);
    }
}

export function getApplicationsPage(page: Page) {
    return new ApplicationPage(page);
}
