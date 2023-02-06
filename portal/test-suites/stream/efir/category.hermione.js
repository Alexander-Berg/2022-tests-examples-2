'use strict';

const {PAGEDATA, getClassName} = require('./PAGEDATA');

const categoryTest = function (path = PAGEDATA.url.path) {
    var screenName = PAGEDATA.classNames.screens.category;
    var category = PAGEDATA.classNames.category;

    async function testBefore(type) {
        var categoryType;

        if (type === 'film') {
            categoryType = PAGEDATA.url.getParams.categoryFilm;
        }

        if (type === 'series') {
            categoryType = PAGEDATA.url.getParams.categorySeries;
        }

        await this.browser.yaOpenMorda({
            path: path,
            getParams: categoryType
        });

        await this.browser.$(screenName).then(elem => elem.waitForDisplayed());
        const streamClassName = await this.browser.$(PAGEDATA.classNames.stream).then(elem => elem.getAttribute('className'));
        streamClassName.should.have.string(getClassName(PAGEDATA.classNames.active.category));
        return this.browser.$(category.feed).then(elem => elem.waitForDisplayed());
    }

    describe('Список фильмов открывается', function () {
        it.skip('Включен правильный экран, основные элементы присутствуют', function () {
            return this.browser.then(testBefore.bind(this, 'film'));
        });
    });

    describe('Список сериалов открывается', function () {
        it.skip('Включен правильный экран, основные элементы присутствуют', function () {
            return this.browser.then(testBefore.bind(this, 'series'));
        });
    });
};

specs('Экран со списком по категории', function () {
    categoryTest();
});

module.exports = {
    categoryTest
};

