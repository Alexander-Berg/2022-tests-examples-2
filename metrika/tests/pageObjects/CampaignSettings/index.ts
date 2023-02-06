import { Browser } from 'hermione';
import { isUndefined } from 'lodash';
import { Page } from '../Page';
import { testIds, createClassSelector, createIdSelector } from 'shared/testIds';
import { DescriptionPage } from './pages/description';
import { GoalsPage } from './pages/goals';
import { PlanPage } from './pages/plan';
import { PlacementsPage } from './pages/placements';
import { ConfirmModal } from 'tests/pageObjects/ConfirmModal';

class CampaignSettings extends Page {
    descriptionPage: DescriptionPage;
    goalsPage: GoalsPage;
    planPage: PlanPage;
    placementsPage: PlacementsPage;
    confirmModal: ConfirmModal;

    constructor(browser: Browser) {
        super(browser);

        this.descriptionPage = new DescriptionPage(browser);
        this.goalsPage = new GoalsPage(browser);
        this.planPage = new PlanPage(browser);
        this.placementsPage = new PlacementsPage(browser);
        this.confirmModal = new ConfirmModal(browser);
    }

    get nextButton() {
        return this.browser.$(createClassSelector(testIds.campaign.edit.next));
    }

    get saveButton() {
        return this.browser.$(createIdSelector(testIds.campaign.edit.save));
    }

    get deleteButton() {
        return this.browser.$(
            createClassSelector(testIds.campaign.edit.delete),
        );
    }

    async waitUntilSave() {
        return this.browser.waitUntil(async () => {
            const cls = await this.saveButton.getAttribute<string>('class');

            return !cls.includes('button2_progress_yes');
        });
    }

    async saveChanges() {
        await this.saveButton.click();
        await this.waitUntilSave();
    }

    async deleteCampaign() {
        await this.deleteButton.click();
        await this.confirmModal.confirm();
    }

    open(id?: string) {
        if (isUndefined(id)) {
            return this.browser.url('campaign/new');
        }

        return this.browser.url(`/advertiser/${id}`);
    }
}

export { CampaignSettings };
