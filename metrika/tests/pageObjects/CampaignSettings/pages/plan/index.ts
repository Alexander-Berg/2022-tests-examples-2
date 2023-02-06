import { Page } from 'tests/pageObjects/Page';
import { createIdSelector, testIds, createClass } from 'shared/testIds';
import { Chance } from 'chance';

const chance = new Chance();

const goalItemClass = createClass(testIds.campaign.edit.plan.goal);

class PlanPage extends Page {
    get randomValue() {
        return chance.integer({
            min: 0,
            max: 100,
        });
    }

    get clicksInput() {
        return this.browser.$(
            createIdSelector(testIds.campaign.edit.plan.clicks),
        );
    }

    get conversionCostInput() {
        return this.browser.$(
            createIdSelector(testIds.campaign.edit.plan.conversionCost),
        );
    }

    get conversionsInput() {
        return this.browser.$(
            createIdSelector(testIds.campaign.edit.plan.conversions),
        );
    }

    get cpcInput() {
        return this.browser.$(createIdSelector(testIds.campaign.edit.plan.cpc));
    }

    get cpmInput() {
        return this.browser.$(createIdSelector(testIds.campaign.edit.plan.cpm));
    }

    get ctrInput() {
        return this.browser.$(createIdSelector(testIds.campaign.edit.plan.ctr));
    }

    get showsInput() {
        return this.browser.$(
            createIdSelector(testIds.campaign.edit.plan.shows),
        );
    }

    get goalsSelectButton() {
        return this.browser.$(
            createIdSelector(testIds.campaign.edit.plan.goalButton),
        );
    }

    getGoal(name: string) {
        return this.browser.$(
            `.//*[contains(@class, "${goalItemClass}")]//*[text()="${name}"]`,
        );
    }

    async selectGoal(name: string) {
        await this.goalsSelectButton.click();
        await this.getGoal(name).click();
    }

    async clearFullForm() {
        await this.clearGoalPlan();
        await this.clearCommonPlan();
    }

    async fillFullForm(name: string) {
        await this.fillGoalPlan(name);

        await this.fillCommonPlan();
    }

    async clearGoalPlan() {
        await this.conversionsInput.customClearValue();
        await this.conversionCostInput.customClearValue();
    }

    async fillGoalPlan(name: string) {
        await this.selectGoal(name);
        await this.conversionsInput.setValue(this.randomValue);
        await this.conversionCostInput.setValue(this.randomValue);
    }

    async clearCommonPlan() {
        await this.showsInput.customClearValue();
        await this.clicksInput.customClearValue();
        await this.ctrInput.customClearValue();
        await this.cpmInput.customClearValue();
        await this.cpcInput.scroll(0, 300);
        await this.cpcInput.customClearValue();
    }

    async fillCommonPlan() {
        await this.showsInput.setValue(this.randomValue);
        await this.clicksInput.setValue(this.randomValue);
        await this.ctrInput.setValue(this.randomValue);
        await this.cpmInput.setValue(this.randomValue);
        await this.cpcInput.scroll(0, 300);
        await this.cpcInput.setValue(this.randomValue);
    }

    open(advertiserId: number, campaignId: number) {
        return this.browser.url(
            `/advertiser/${advertiserId}/campaign/${campaignId}/edit/plan`,
        );
    }

    async collectGoalPlan() {
        return {
            goal: await this.goalsSelectButton.getText(),
            convertsions: await this.conversionsInput.getValue(),
            conversionCost: await this.conversionCostInput.getValue(),
        };
    }

    async collectCommonPlan() {
        return {
            shows: await this.showsInput.getValue(),
            clicks: await this.clicksInput.getValue(),
            ctr: await this.ctrInput.getValue(),
            cpm: await this.cpmInput.getValue(),
            cpc: await this.cpcInput.getValue(),
        };
    }

    async collectFullForm() {
        return {
            ...(await this.collectCommonPlan()),
            ...(await this.collectGoalPlan()),
        };
    }

    waitForLoad() {
        return this.cpcInput.customWaitForExist();
    }
}

export { PlanPage };
