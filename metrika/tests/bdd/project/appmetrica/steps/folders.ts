import {When, Then} from "@cucumber/cucumber";
import {assert, expect} from "chai";
import { OurWorld } from "../../../types";

When("I create a new folder with name {string}", async function (this: OurWorld, keys: string) {
    await this.appmetrica.applicationsPage.appsMenuFragment.addFolderButton.delay(1500);
    await this.appmetrica.applicationsPage.appsMenuFragment.addFolderButton.click();
    const folder = (
        await this.appmetrica.applicationsPage.appsMenuFragment.foldersFragment.foldersList.init()
    ).get(0);// when you create a new folder it is always first (index 0) in folders list until you confirm creation
    await folder.folderClearInput.click();
    await folder.folderNameInput.fill(keys);
    await folder.saveFolder.click();
    }
);

When("I delete a folder with name {string}", async function (this: OurWorld, keys: string) {
    await this.appmetrica.applicationsPage.appsMenuFragment.foldersFragment.delay(1500);
    const folder = (
        await this.appmetrica.applicationsPage.appsMenuFragment.foldersFragment.foldersList.init()
    ).getByName(keys);
    await folder.locator.hover();
    await folder.editFolder.click();
    await folder.deleteFolder.click();
});


When("I click on the empty folder with name {string}", async function (this: OurWorld, keys: string) {
    await this.appmetrica.applicationsPage.appsMenuFragment.foldersFragment.delay(1000);
    const folder = await (
        await this.appmetrica.applicationsPage.appsMenuFragment.foldersFragment.foldersList.init()).getByName(keys);
    await folder.folderButton.click();
    await this.appmetrica.applicationsPage.appsMenuFragment.foldersFragment.delay(1000);
    }
);

When("I remove an app with name {string} from a folder with name {string}",
    async function (this: OurWorld, appName: string, folderName: string) {
        await this.appmetrica.applicationsPage.appsMenuFragment.foldersFragment.delay(1500);
        const currentFolder = (await this.appmetrica.applicationsPage.appsMenuFragment
            .foldersFragment.foldersList.init()).getByName(folderName);
        if(!await currentFolder.folderIconOpened.isVisible()){
            await currentFolder.folderButton.click();
        }
        const appInFolder = await (await this.appmetrica.applicationsPage.appsMenuFragment
            .appsListInFolders.appsList.init()).getByName(appName);
        await appInFolder.locator.hover();
        await appInFolder.changeFolder.click();
        const selectedFolder =
            await (await this.appmetrica.applicationsPage.popupChangeFolderFragment.init()).getByName(folderName);
        await selectedFolder.click();
        await this.appmetrica.applicationsPage.appsMenuFragment.appsList.delay(1000);
    }
);

When("I put an app with name {string} from the applist to a folder with name {string}",
    async function (this: OurWorld, appName: string, folderName: string) {
        await this.appmetrica.applicationsPage.appsMenuFragment.foldersFragment.delay(1500);
        const selectedApp =
            (await this.appmetrica.applicationsPage.appsMenuFragment.appsList.appsList.init()).getByName(appName);
        await selectedApp.locator.hover();
        await selectedApp.changeFolder.click();
        const selectedFolder =
            (await this.appmetrica.applicationsPage.popupChangeFolderFragment.init()).getByName(folderName);
        await selectedFolder.click();
    }
);

Then("I see the empty folder report for the folder", async function (this: OurWorld) {
    await this.appmetrica.applicationsPage.reportFragment.emptyFolderReport.delay(1500);
    const element = await this.appmetrica.applicationsPage.reportFragment.emptyFolderReport.locator.isVisible();
    assert.equal( element, true, "The element is visible");
    }
);

Then("I see a folder with name {string} in the folders list", async function (this: OurWorld, expectedFolderName: string) {
    await this.appmetrica.applicationsPage.appsMenuFragment.foldersFragment.delay(1500);
    const actualFolderName =
        await this.appmetrica.applicationsPage.appsMenuFragment.foldersFragment.getFolderNames();
    assert.include(actualFolderName, expectedFolderName, "the folder in the folders list");
    }
);

Then("I do not see a folder with name {string}", async function (this: OurWorld, expectedFolderName: string) {
    await this.appmetrica.applicationsPage.appsMenuFragment.foldersFragment.delay(1500);
    const actualFolderName =
        await this.appmetrica.applicationsPage.appsMenuFragment.foldersFragment.getFolderNames();
    expect(actualFolderName).not.include(expectedFolderName, "the folder doesn't in the list");
    }
);

Then("I see the app {string} in a folder with name {string}", async function (this: OurWorld, appName: string, folderName: string) {
    await this.appmetrica.applicationsPage.appsMenuFragment.foldersFragment.delay(1500);
    const foldersList = await this.appmetrica.applicationsPage.appsMenuFragment.foldersFragment.foldersList.init();
    await (await foldersList.getByName(folderName)).folderButton.click();
    const appInFolder = await (await (await this.appmetrica.applicationsPage.appsMenuFragment.
        appsListInFolders.appsList.init()).getByName(appName)).isVisible();
    assert.equal(appInFolder, true, "The app exists in the desired folder");
    }
);
