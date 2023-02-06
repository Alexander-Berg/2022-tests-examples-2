import { When, Then } from "@cucumber/cucumber";
import { assert } from "chai";
import { OurWorld } from "../../../types";

When("I open the app {string}", async function (this: OurWorld, appName: string) {
        const app = (
            await this.appmetrica.applicationsPage.appsMenuFragment.appsList.appsList.init()
        ).getByName(appName);
        await app.click();
    }
);

When("I search {string} app", async function (this: OurWorld, appName: string) {
    await this.appmetrica.applicationsPage.appsMenuFragment.searchField.fill(appName);
    await this.appmetrica.applicationsPage.appsMenuFragment.delay(1000);
});

Then("I see {int} reports", async function (this: OurWorld, expectedNumber) {
    await this.appmetrica.applicationsPage.reportFragment.reportTitle.waitForVisible();
    const reports =
        await this.appmetrica.applicationsPage.reportsMenuFragment.reportButtons.init();
    const actualNumber = reports.size();
    assert.equal(actualNumber, expectedNumber, "the number of reports is equal");
});

Then("I see {int} report groups", async function (this: OurWorld, expectedNumber) {
    await this.appmetrica.applicationsPage.reportFragment.reportTitle.waitForVisible();
    const groups = await this.appmetrica.applicationsPage.reportsMenuFragment.reportGroups.init();
    const actualNumber = groups.size();
    assert.equal(actualNumber, expectedNumber, "the number of groups is equal");
});

Then("I see {string} in the app list", async function (this: OurWorld, expectedAppName: string) {
    await this.appmetrica.applicationsPage.appsMenuFragment.appsList.delay(1000);
    const actualAppName =
        await this.appmetrica.applicationsPage.appsMenuFragment.appsList.getAppNames();
    assert.include(actualAppName, expectedAppName, "the app in the app list");
    }
);

Then("I see {string} in the search result", async function (this: OurWorld, expectedAppName: string) {
        const searchResult =
            await this.appmetrica.applicationsPage.appsMenuFragment.getElementByText(expectedAppName);
        const actualAppName = await searchResult.getText();
        assert.include(actualAppName, expectedAppName, "search result contains app");
    }
);
