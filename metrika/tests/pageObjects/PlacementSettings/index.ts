import { Browser } from 'hermione';
import { Page } from 'tests/pageObjects/Page';
import { testIds, createIdSelector } from 'shared/testIds';
import { SearchSelect } from 'tests/pageObjects/SearchSelect';
import { LandingsEditForm } from 'tests/pageObjects/LandingEditForm';

class PlacementSettings extends Page {
    landingSelect: SearchSelect;
    siteSelect: SearchSelect;
    landingCreateForm: LandingsEditForm;

    constructor(browser: Browser) {
        super(browser);

        this.landingCreateForm = new LandingsEditForm(browser);
        this.landingSelect = new SearchSelect(
            browser,
            testIds.placement.landing,
        );
        this.siteSelect = new SearchSelect(browser, testIds.placement.site);
    }

    get nameInput() {
        return this.browser.$(createIdSelector(testIds.placement.name));
    }

    get costInput() {
        return this.browser.$(createIdSelector(testIds.placement.cost));
    }

    get volumeInput() {
        return this.browser.$(createIdSelector(testIds.placement.volume));
    }

    get newLandingButton() {
        return this.browser.$(createIdSelector(testIds.placement.landingNew));
    }

    get saveButton() {
        return this.browser.$(createIdSelector(testIds.placement.saveButton));
    }

    async createPlacement() {
        await this.nameInput.setValue('test');

        await this.newLandingButton.click();
        await this.landingCreateForm.fillFormWithRandomValues();
        await this.landingCreateForm.saveAndClose();

        await this.siteSelect.selectName('Яндекс.Директ');

        await this.volumeInput.setValue(12);
        await this.costInput.setValue(12);

        await this.saveButton.click();
    }
}

export { PlacementSettings };
