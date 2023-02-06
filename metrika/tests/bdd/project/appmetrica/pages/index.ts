import { Page } from "playwright";
import { ApplicationPage, getApplicationsPage } from "./applications";
import { AddNewAppPage, getAddNewAppPage} from "./addNewApp";
import {AudiencePage, CommonPage, getAudiencePage, getCommonPage, getUAPage, UAPage,} from "./reports";

export class Appmetrica {
    page: Page;
    applicationsPage: ApplicationPage;
    addNewAppPage: AddNewAppPage;
    audiencePage: AudiencePage;
    uaPage: UAPage;
    commonReportPage: CommonPage;

    constructor(page: Page) {
        this.page = page;
        this.applicationsPage = getApplicationsPage(this.page);
        this.addNewAppPage = getAddNewAppPage(this.page);
        this.audiencePage = getAudiencePage(this.page);
        this.uaPage = getUAPage(this.page);
        this.commonReportPage = getCommonPage(this.page);
    }
}
