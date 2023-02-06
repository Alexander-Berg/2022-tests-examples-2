import { Given, Then, When } from "@cucumber/cucumber";
import { assert } from "chai";

import { OurWorld } from "../../../types";

Given("I open reports for {int} application id", async function (this: OurWorld, appId: number) {
        await this.appmetrica.applicationsPage.gotoReport(appId);
        await this.appmetrica.applicationsPage.reportFragment.reportTitle.waitForVisible();
    }
);

When("I click {string} report", async function (this: OurWorld, reportName: string) {
        const reportButton =
            await this.appmetrica.applicationsPage.reportsMenuFragment.getReportByName(reportName);
        await reportButton.click();
        await this.appmetrica.applicationsPage.waitForReport();
    }
);

Then("I see an {string} report", async function (this: OurWorld, expectedTitle: string) {
        const actualTitle = await this.appmetrica.applicationsPage.reportFragment.reportTitle.getText();
        assert.equal(actualTitle, expectedTitle, "titles are equal");
    }
);
