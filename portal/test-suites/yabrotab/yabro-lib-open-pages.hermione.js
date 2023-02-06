'use strict';
const {hide} = require('./utils');

const defaultGetParams = {
    mordaEnabled: true,
    zenEnabled: true,
    pageVisible: true,
    browserExperiments: '{}',
    pageMode: 'custo',
    theme: 'light',
    tabloSize: 'auto',
    tabloItems: 3,
    autoPageMode: true,
    zenLibEnv: 'stable'
};

async function openMordaLib(params) {
    await this.browser.yaOpenMorda({
        path: '/portal/front/morda-lib',
        getParams: {
            ...defaultGetParams,
            ...params
        },
        hasShowid: false
    });

    await this.browser.yaHideElement(hide);
    await this.browser.$('.test-page_lib_loaded').then(elem => elem.waitForExist({
        timeout: 5000
    }));
    return this.browser.$('.bro-zen_loading_yes').then(elem => elem.waitForExist({
        timeout: 2000,
        reverse: true
    }));
}

function setParamValue(name, value) {
    return this.executeAsync(function (name, value, done) {
        window.setParamValue(name, value);

        // TODO дождаться окончания изменений.
        requestAnimationFrame(() => {
            done();
        });
    }, name, value)
        .catch(e => {
            e.message = `setParamValue(${name}, ${value}): ${e.message}`;
            throw e;
        });
}

function getParamValue(name) {
    return this.yaInBrowser(function (name) {
        return window.getParamValue(name);
    }, name)
        .catch(e => {
            e.message = `getParamValue(${name}): ${e.message}`;
            throw e;
        });
}


function scrollToTab() {
    return this.yaInBrowser(function () {
        const height = window.innerHeight;
        window.scrollTo(0, height);
    }).catch(e => {
        e.message = `scrollToTab: ${e.message}`;
        throw e;
    });
}

specs('yabro-lib-open-pages', function () {
    beforeEach(async function setupRegion() {
        await this.browser.yaOpenMorda({
            path: '/empty.html'
        });

        await this.browser.yaSetRegion(213, {reload: false});
    });

    describe('ресайз', function () {
        function setReduced() {
            return this.browser.yaSetViewportSize({
                width: 950,
                height: 900
            });
        }
        function setNormal() {
            return this.browser.yaSetViewportSize({
                width: 1100,
                height: 900
            });
        }
        function setEnlarged() {
            return this.browser.yaSetViewportSize({
                width: 1250,
                height: 900
            });
        }

        function normalLayout() {
            return this.browser.yaGeometry(({expect}) => {
                expect('.weather2').to.be.toTheRightOf('.news');

                expect('.traffic').not.to.be.visible()
                    .or.to.be.toTheRightOf('.news')
                    .and.to.be.under('.weather2');

            });
        }

        function wideLayout() {
            return this.browser.yaGeometry(({expect}) => {
                expect('.weather2').to.be.toTheRightOf('.news');

                expect('.traffic').not.to.be.visible()
                    .or.to.be.toTheRightOf('.news');

                expect('.traffic').not.to.be.visible()
                    .or.to.be.toTheRightOf('.weather2')
                    .or.to.be.under('.weather2');

            });
        }

        describe('из нормального', function () {
            beforeEach(async function () {
                await setNormal.call(this);
                return openMordaLib.call(this);
            });

            describe('в уменьшенный', function () {
                beforeEach(function() {
                    return setReduced.call(this);
                });

                it('меняется раскладка', function () {
                    return normalLayout.call(this);
                });

                it.skip('после переоткрытия перестраивается дзен', async function () {
                    await this.browser.yaGeometry(({expect}) => {
                        expect('.feed__row:first-child .feed__item-wrap')
                            .to.have.lengthOf(2);
                    });
                    // TODO дзене сейчас не работает
                });
            });

            describe('в увеличенный', function () {
                beforeEach(function () {
                    return setEnlarged.call(this);
                });


                it('широкая раскладка', function () {
                    return wideLayout.call(this);
                });

                it('всё скейлится на 1.2', async function() {
                    await this.browser.yaGeometry(({expect}) => {
                        expect('.main').to.have.width(1024);
                    });
                });
            });
        });

        describe('из уменьшенного в нормальный', function () {
            beforeEach(async function () {
                await setReduced.call(this);
                await openMordaLib.call(this);
                await setNormal.call(this);
            });

            it('меняется раскладка', function () {
                return wideLayout.call(this);
            });
        });

        describe('из увеличенного в нормальный', function () {
            beforeEach(async function () {
                await setEnlarged.call(this);
                await openMordaLib.call(this);
                await setNormal.call(this);
            });

            it('широкая раскладка', function () {
                return wideLayout.call(this);
            });

            it('всё скейлится к 1', async function() {
                await this.browser.yaGeometry(({expect}) => {
                    expect('.main').to.have.width(856);
                });
            });
        });
    });

    describe('скролл в таб', () => {
        beforeEach(function () {
            return openMordaLib.call(this)
                .then(() => scrollToTab.call(this.browser));
        });

        it('поскроллилось в таб', async function () {
            const mode = await getParamValue.call(this.browser, 'pageMode');
            mode.should.equal('tab');
            const scroll = await this.browser.yaInBrowser(() => window.scrollY);
            scroll.should.be.greaterThan(50);
        });

        it('клик в стрелку скроллит в начало', async function () {
            await this.browser.yaSetViewportSize({
                width: 1600,
                height: 800
            });

            await this.browser.$('.bro-scroll-button').then(elem => elem.click());
            const scroll = await this.browser
                .yaInBrowser(() => {
                    return new Promise(resolve => {
                        const start = Date.now();
                        function tryScroll() {
                            if (window.scrollY &&
                                Date.now() - start < 2000) {
                                return requestAnimationFrame(tryScroll);
                            }
                            resolve(window.scrollY);
                        }

                        requestAnimationFrame(tryScroll);
                    });
                });
            scroll.should.be.lessThan(5);
        });

        it('стрелка вверх показывается, когда места хватает', async function () {
            await this.browser.yaSetViewportSize({
                width: 1600,
                height: 800
            });
            const visible = await this.browser.$('.bro-scroll-button').then(elem => elem.isDisplayed());
            visible.should.be.true;
        });

        it('стрелка вверх не показывается, когда места не хватает', async function () {
            await this.browser.yaSetViewportSize({
                width: 1000,
                height: 800
            });
            const visible = await this.browser.$('.bro-scroll-button').then(elem => elem.isDisplayed());
            visible.should.be.false;
        });
    });

    describe.skip('включение/выключение элементов морды', () => {
        const turnMordaOn = (func) => {
                describe('включение морды', () => {
                    beforeEach(function () {
                        return setParamValue.call(this.browser, 'mordaEnabled', true);
                    });

                    it('морда включилась', async function() {
                        await this.browser.yaGeometry(({expect}) => {
                            expect('.main').to.be.visible();
                        });
                    });

                    if (func) {
                        func();
                    }
                });
            },
            turnMordaOff = (func) => {
                describe('выключение морды', () => {
                    beforeEach(function () {
                        return setParamValue.call(this.browser, 'mordaEnabled', true);
                    });

                    it('морда выключилась', async function() {
                        await this.browser.yaGeometry(({expect}) => {
                            expect('.main').not.to.be.visible();
                        });
                    });

                    if (func) {
                        func();
                    }
                });
            },
            turnZenOn = (func) => {
                describe('включение дзена', () => {
                    beforeEach(function () {
                        return setParamValue.call(this.browser, 'zenEnabled', true);
                    });

                    it('дзен включился', async function() {
                        await this.browser.yaGeometry(({expect}) => {
                            expect('.bro-zen').to.be.visible();
                        });
                    });

                    if (func) {
                        func();
                    }
                });
            },
            turnZenOff = (func) => {
                describe('выключение дзена', () => {
                    beforeEach(function () {
                        return setParamValue.call(this.browser, 'zenEnabled', true);
                    });

                    it('дзен выключился', async function() {
                        await this.browser.yaGeometry(({expect}) => {
                            expect('.bro-zen').not.to.be.visible();
                        });
                    });

                    if (func) {
                        func();
                    }
                });
            };

        describe('создание с дзеном и с мордой', () => {
            beforeEach(function openPage() {
                return openMordaLib.call(this, {
                    zenEnabled: true,
                    mordaEnabled: true
                });
            });

            turnMordaOff(() => {
                turnMordaOn();

                turnZenOff(() => {
                    turnMordaOn(() => {
                        turnZenOn();
                    });

                    turnZenOn(() => {
                        turnMordaOn();
                    });
                });
            });

            turnZenOff(() => {
                turnZenOn();

                turnMordaOff(() => {
                    turnMordaOn(() => {
                        turnZenOn();
                    });

                    turnZenOn(() => {
                        turnMordaOn();
                    });
                });
            });
        });

        describe('создание с мордой без дзена', () => {
            beforeEach(function openPage() {
                return openMordaLib.call(this, {
                    zenEnabled: false,
                    mordaEnabled: true
                });
            });

            turnZenOn(() => {
                turnZenOff();
            });

            turnMordaOff(() => {
                turnMordaOn();
            });
        });

        describe('создание с дзеном без морды', () => {
            beforeEach(function openPage() {
                return openMordaLib.call(this, {
                    zenEnabled: true,
                    mordaEnabled: false
                });
            });

            turnZenOff(() => {
                turnZenOn();
            });

            turnMordaOn(() => {
                turnMordaOff();
            });
        });

        describe('создание без дзена и морды', () => {
            beforeEach(function openPage() {
                return openMordaLib.call(this, {
                    zenEnabled: false,
                    mordaEnabled: false
                });
            });

            turnMordaOn(() => {
                turnMordaOff();

                turnZenOn(() => {
                    turnMordaOff(() => {
                        turnZenOff();
                    });

                    turnZenOff(() => {
                        turnMordaOff();
                    });
                });
            });

            turnZenOn(() => {
                turnZenOff();

                turnMordaOff(() => {
                    turnMordaOff(() => {
                        turnZenOff();
                    });

                    turnZenOff(() => {
                        turnMordaOff();
                    });
                });
            });
        });
    });

    describe('cмена видимости страницы', () => {
        describe('скрытие страницы', () => {
            it.skip('-');
        });

        describe('показ страницы', () => {
            it.skip('отправляется статистика');
            it.skip('запрашиваются данные, если протухли');
            it.skip('не запрашиваются данные, если свежие');
            it('запрашивается баннер');
        });
    });

    describe('смена темы', () => {
        describe('с тёмной на светлую', () => {
            it.skip('красится плашка дзена');
        });

        describe('со светлой на тёмную', () => {
            it.skip('красится плашка дзена');
        });
    });

    describe('изменение гео', () => {
        it.skip('запрашиваются данные');
        it.skip('еняется город в новостях, пробках, погоде');
    });

    describe('изменение языка', () => {
        it.skip('запрашиваются данные');
    });

    describe('изменение авторизации', () => {
        it.skip('запрашиваются данные');
    });
});
