import { Given, When } from "@cucumber/cucumber";
import { authorize } from "../../../lib";
import { OurWorld } from "../../../types";

Given("Authorize as {string}", async function (this: OurWorld, login: string) {
    await authorize(this.page, login);
    await this.appmetrica.applicationsPage.goto(`${global.baseAppmetricaUrl}/application/list`);
});

When("I open url {string}", async function (this: OurWorld, url: string) {
    await this.appmetrica.applicationsPage.goto(`${global.baseAppmetricaUrl}${url}`);
});
