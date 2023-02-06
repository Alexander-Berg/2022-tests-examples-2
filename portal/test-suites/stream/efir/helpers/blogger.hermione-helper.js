'use strict';

const {PAGEDATA, getClassName} = require('../PAGEDATA');

const bloggerTest = function (path = PAGEDATA.url.path) {
    var screenName = PAGEDATA.classNames.screens.blogger;
    var blogger = PAGEDATA.classNames.blogger;

    describe('Страница блогера открывается', function () {
        it('включен правильный экран, выделен таб каналов', async function() {
            await this.browser.yaOpenMorda({
                path: path,
                getParams: PAGEDATA.url.getParams.blogger
            });

            await this.browser.$(screenName).then(elem => elem.waitForDisplayed());
            await this.browser.$(blogger.header).then(elem => elem.waitForDisplayed());
            await this.browser.$(blogger.topImage).then(elem => elem.waitForDisplayed());
            await this.browser.$(blogger.headerInfo).then(elem => elem.waitForDisplayed());
            await this.browser.$(blogger.items).then(elem => elem.waitForDisplayed());
            const streamClassName = await this.browser.$(PAGEDATA.classNames.stream).then(elem => elem.getAttribute('className'));
            streamClassName.should.have.string(getClassName(PAGEDATA.classNames.active.blogger));
            const tabClassName = await this.browser.$(PAGEDATA.classNames.header.tabs.blogger).then(elem => elem.getAttribute('className'));
            tabClassName.should.have.string(getClassName(PAGEDATA.classNames.header.tabs.active));
        });

    });

};

module.exports = {
    bloggerTest
};

