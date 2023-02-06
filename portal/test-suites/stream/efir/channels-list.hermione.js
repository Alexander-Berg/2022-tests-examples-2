'use strict';

const {PAGEDATA, getClassName} = require('./PAGEDATA');

const channelsListTest = function (path = PAGEDATA.url.path) {
    var screenName = PAGEDATA.classNames.screens.channelsList;
    var tagList = PAGEDATA.classNames.taglist;
    var channelsList = PAGEDATA.classNames.channelsList;

    describe('Страница со списком каналов открывается', function () {
        it.skip('Включен правильный экран, основные элементы присутствуют', async function() {
            await this.browser.yaOpenMorda({
                path: path,
                getParams: PAGEDATA.url.getParams.channelsList
            });

            await this.browser.$(screenName).then(elem => elem.waitForDisplayed());
            const streamClassName = await this.browser.$(PAGEDATA.classNames.stream).then(elem => elem.getAttribute('className'));
            streamClassName.should.have.string(getClassName(PAGEDATA.classNames.active.channelsList));
            await this.browser.$(channelsList.categories).then(elem => elem.waitForDisplayed());
            await this.browser.$(channelsList.content).then(elem => elem.waitForDisplayed());
            await this.browser.$(tagList.className).then(elem => elem.waitForDisplayed());
            await this.browser.$(tagList.itemKey).then(elem => elem.waitForDisplayed());
            await this.browser.$(tagList.itemContent).then(elem => elem.waitForDisplayed());
        });

    });

};

specs('Экран со списком каналов', function () {
    channelsListTest();
});

module.exports = {
    channelsListTest
};

