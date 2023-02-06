import { When } from "@cucumber/cucumber";
import { OurWorld } from "../../../types";

When("I create an app with name {string}", async function (this: OurWorld, appName: string) {
    const firstForm = this.appmetrica.addNewAppPage.addNewAppFragment.firstForm;
    const secondForm = this.appmetrica.addNewAppPage.addNewAppFragment.secondForm;
    const thirdForm = this.appmetrica.addNewAppPage.addNewAppFragment.thirdForm;

    await firstForm.inputAppName.fill(appName);
    await firstForm.popupCategoryButton.click();
    const selectedCategory = (await this.appmetrica.addNewAppPage
        .popupAppCategoryFragment.dropDownSelector.init()).get(5);
    await selectedCategory.waitForVisible();
    await selectedCategory.click();

    await firstForm.buttonContinue.click();
    await secondForm.buttonAddApp.click();
    await thirdForm.delay(1000);
    if (await thirdForm.buttonGoToReports.isVisible()){
        await thirdForm.buttonGoToReports.click();
        await this.appmetrica.applicationsPage.reportsMenuFragment.appsListButton.waitForVisible();
        await this.appmetrica.applicationsPage.reportsMenuFragment.appsListButton.click();
        }
    }
);

When("I delete an app with name {string} from the app list", async function (this: OurWorld, appName: string) {
    await this.appmetrica.applicationsPage.goto(`${global.baseAppmetricaUrl}/application/list`);
    const selectedApp = await (await this.appmetrica.applicationsPage.appsMenuFragment
        .appsList.appsList.init()).getByName(appName);
    await selectedApp.locator.hover();
    await selectedApp.settingButton.click();
    await this.appmetrica.page.locator(".button.application-settings__remove-button").click();
    }
);
