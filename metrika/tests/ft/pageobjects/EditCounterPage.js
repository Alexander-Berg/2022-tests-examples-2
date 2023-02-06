const Page = require('./Page.js');

const saveChanges = '.counter-edit_has-changes_yes .counter-edit__counter-buttons button';

const firstGoal = '.counter-edit-table__items tr .counter-edit-table-row__drag';
const goalDestination = '.counter-edit-table__items tr:last-child';

const counterRemoveButton = '.counter-edit__remove-button';
const confirmPopupButton = '.popup__content .button_action_confirm';

//popups
const modalPopup = '.popup_type_modal .popup__content';
const popupSelect = '.popup .select__list';

//selectors for goal tab
const createGoal = '.counter-edit-table__add-btn';
const createGoalTitle = '.counter-edit-goal__goal-name-input span input';
const retargeting = '.counter-edit-goal__retargeting [type="checkbox"]'
const goalId = '.counter-edit-table-row__goal-id-column';
const urlGoalValue = '.counter-edit-table-row_type_goal-condition input';
const compositeGoalTab = '#goal-types-panes-tab-3 input';
const compositeGoalStepName = '.counter-edit-goal-steps-list-item__step-name input';
const compositeGoalValue = '.tabs-panes__pane_active_yes .counter-edit-table-row__value-column input';
const goalCreateButton = '.button_action_validate';

//selectors for grants tab
const createGrantBtn = '.counter-edit-grants__users-access .counter-edit-table__controls .counter-edit-table__add-btn';
const grantedUserName = '.counter-edit-grant__user-input input';
const grantPermSelect = '.counter-edit-grant__cell button';
const grantEditPerm = '.popup_type_modal .select__list .select__item:last-child .select__text';
const grantViewPerm = '.popup_type_modal .select__list .select__item:first-child .select__text';
const addGrantBtn = '.button_action_validate';
const grantLoginRow = '.counter-edit-table-row__user-column';
const grantPermRow = '.counter-edit-table-row__access-column';

class EditCounterPage extends Page {
    async open(counterId) {
        await this.browser.url(`/settings?id=${counterId}`);
    }

    async openGoals(counterId) {
        await this.browser.url(`/goals/?id=${counterId}`)
            .waitForExist(createGoal);
    }

    async openGrants(counterId) {
        await this.browser.url(`/settings?id=${counterId}&tab=grants`)
            .waitForExist(createGrantBtn);
    }

    async createUrlGoal(isRetagreting) {
        await this.browser.click(createGoal)
            .waitForExist(createGoalTitle);
        if (isRetagreting) {
            await this.browser.click(retargeting);
        }
        await this.fillGoalName();
        await this.browser
            .element(urlGoalValue)
            .setValue(this.getRandomString(10))
            .click(goalCreateButton)
            .pause(2000)
            .refresh()
            .waitForExist(createGoal);
    }

    async createCompositeGoal(isRetagreting) {
        await this.browser.click(createGoal)
            .waitForExist(createGoalTitle);
        if (isRetagreting) {
            await this.browser.click(retargeting);
        }
        await this.fillGoalName();
        await this.browser
            .click(compositeGoalTab)
            .waitForExist(compositeGoalStepName)
            .element(compositeGoalStepName)
            .setValue(this.getRandomString(10))
            .waitForEnabled(compositeGoalValue)
            .element(compositeGoalValue)
            .setValue(this.getRandomString(10))
            .click(goalCreateButton)
            .pause(2000)
            .refresh()
            .waitForExist(createGoal);
    }


    async fillGoalName() {
        await this.browser
            .element(createGoalTitle)
            .setValue(`Тестовая цель ${this.getRandomString(10)}`);
    }

    async changeGoalsOrder() {
        if (await this.countGoals() > 2) {
            await this.browser.dragAndDrop(firstGoal, goalDestination)
                .waitUntil(function () {
                    return this.isVisible(saveChanges);
                })
                .click(saveChanges);
        } else {
            throw Error('No goals for test');
        }
    }

    async countGoals() {
        let elements = await this.browser
            .elements(goalId);
        return elements.value.length;
    }

    async getGoalIds() {
        let result = [];
        let elements = await this.browser.elements(goalId);
        for (let i = 0; i < elements.value.length; i++) {
            let element = await this.browser.elementIdText(elements.value[i].ELEMENT);
            result.push(await element.value);
        }
        return result;
    }

    async createGrant(user, isEdit) {
        await this.browser.scroll(createGrantBtn)
            .screenshot()
            .click(createGrantBtn)
            .waitForVisible(modalPopup);
        if (isEdit) {
            await this.browser
                .click(grantPermSelect)
                .waitForVisible(popupSelect)
                .click(grantEditPerm)
        } else {
            await this.browser
                .click(grantPermSelect)
                .waitForVisible(popupSelect)
                .click(grantViewPerm)
        }
        await this.browser.element(grantedUserName)
            .setValue(user)
            .click(addGrantBtn)
            .pause(2000);
    }

    async getAllGrants() {
        let result = [];
        let elements = await this.browser.elements(grantLoginRow);
        for (let i = 0; i < elements.value.length; i++) {
            let element = await this.browser.elementIdText(elements.value[i].ELEMENT);
            result.push(await element.value);
        }
        return result;
    }

    async getGrantPermission() {
        return await this.browser
            .getText(grantPermRow);
    }

    async deleteCounter(counterId) {
        await this.open(counterId);
        await this.browser.waitForExist(counterRemoveButton)
            .click(counterRemoveButton)
            .waitForVisible(confirmPopupButton)
            .click(confirmPopupButton)
            .pause(5000)
    }
}

module.exports = {
    EditCounterPage,
};
