const Page = require('./Page.js');

const addCounterButton = '.counters-list__add-counter';

class CounterListPage extends Page {
    async open() {
        await this.browser.url('/list');
    }

    async openAddCounter() {
        await this.browser
            .waitForExist(addCounterButton)
            .click(addCounterButton);
    }
}

module.exports = {
    CounterListPage,
};
