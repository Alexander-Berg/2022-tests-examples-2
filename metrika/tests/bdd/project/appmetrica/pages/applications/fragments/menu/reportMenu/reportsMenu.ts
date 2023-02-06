import { Locator } from "playwright-core";
import {
    BaseComponent,
    ButtonElement,
    Collection,
} from "../../../../../../../lib";

export class ReportMenuFragment extends BaseComponent {
    reportButtons: Collection <BaseComponent>;
    appsListButton: ButtonElement;
    reportGroups: Collection <BaseComponent>;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Apps menu");
        this.appsListButton = new ButtonElement(
            this.locator.locator(".menu-reports__title"),
            this,
            "Return to Apps List"
        );
        this.reportButtons = new Collection(
            this.locator.locator(".menu-reports__item_type_report"),
            this,
            ButtonElement,
            "Reports"
        );
        this.reportGroups = new Collection(
            this.locator.locator(".menu-reports__item_type_group"),
            this,
            ButtonElement,
            "Report groups"
        );
    }

    async getReportByName(reportName: string) {
        try {
            const report = await (await this.reportButtons.init()).getByName(reportName);
            await report.locator.elementHandle({ timeout: global.waitTimeout });
            return report;
        } catch (e) {
            throw `Report "${reportName}" was not found`;
        }
    }
}
