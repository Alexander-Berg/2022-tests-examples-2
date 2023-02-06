const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Remote Control - inline', function () {
    const baseUrl = 'https://metrika.yandex.ru/test/remoteControl/';

    const resourceBaseUrl = 'https://yastatic.net/s3/metrika/1/form-selector/';

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });

    it('Open form selector', function () {
        return (
            this.browser
                .url(`${baseUrl}form.hbs`)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options, done) {
                            window.postMessage(
                                JSON.stringify({
                                    action: 'appendremote',
                                    id: 'form-selector',
                                    inline: true,
                                    appVersion: '1',
                                    lang: 'ru',
                                    fileId: 'form',
                                }),
                                '*',
                            );
                            done();
                        },
                    }),
                )
                // запрос за ресурсом
                .execute(function () {
                    return Array.prototype.slice
                        .call(document.getElementsByTagName('script'))
                        .map((item) => item.src);
                })
                .then(({ value: scripts }) => {
                    chai.expect(
                        scripts.filter(
                            (src) => src === `${resourceBaseUrl}form_ru.js`,
                        ).length,
                    ).to.eq(1, 'can not find script request');
                })
                // select form
                .execute(function () {
                    const form = document.getElementById('form');
                    const [foundedForm] = window.Ya._metrika._u.form.select(
                        window.document,
                    );

                    return form === foundedForm;
                })
                .then(({ value }) => {
                    chai.expect(value).to.eq(true, 'cant select form');
                })
                // closest form
                .execute(function () {
                    const form = document.getElementById('form');
                    const input = document.getElementById('name');
                    const foundedForm =
                        window.Ya._metrika._u.form.closest(input);

                    return form === foundedForm;
                })
                .then(({ value }) => {
                    chai.expect(value).to.eq(true, 'cant find closest form');
                })
                // getData
                .execute(function () {
                    const form = document.getElementById('form');
                    return window.Ya._metrika._u.form.getData(form);
                })
                .then(({ value }) => {
                    chai.expect(value).to.deep.eq(
                        { i: 'form', p: 'F' },
                        'incorrect form data',
                    );
                })
        );
    });

    it('Open button selector', function () {
        return (
            this.browser
                .url(`${baseUrl}button.hbs`)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options, done) {
                            window.postMessage(
                                JSON.stringify({
                                    action: 'appendremote',
                                    id: 'form-selector',
                                    inline: true,
                                    appVersion: '1',
                                    lang: 'ru',
                                    fileId: 'button',
                                }),
                                '*',
                            );
                            done();
                        },
                    }),
                )
                // запрос за ресурсом
                .execute(function () {
                    return Array.prototype.slice
                        .call(document.getElementsByTagName('script'))
                        .map((item) => item.src);
                })
                .then(({ value: scripts }) => {
                    chai.expect(
                        scripts.filter(
                            (src) => src === `${resourceBaseUrl}button_ru.js`,
                        ).length,
                    ).to.eq(1, 'can not find script request');
                })
                // select button
                .execute(function () {
                    const button = document.getElementById('button');
                    const [foundedButton] = window.Ya._metrika._u.button.select(
                        window.document,
                    );

                    return button === foundedButton;
                })
                .then(({ value }) => {
                    chai.expect(value).to.eq(true, 'cant select button');
                })
                // closest button
                .execute(function () {
                    const button = document.getElementById('button');
                    const text = document.getElementById('text');
                    const foundedButton =
                        window.Ya._metrika._u.button.closest(text);

                    return button === foundedButton;
                })
                .then(({ value }) => {
                    chai.expect(value).to.eq(true, 'cant find closest button');
                })
                // getData
                .execute(function () {
                    const button = document.getElementById('button');
                    return window.Ya._metrika._u.button.getData(button);
                })
                .then(({ value }) => {
                    chai.expect(value).to.deep.eq(
                        { i: 'button', p: '?', c: '2302977997' },
                        'incorrect button data',
                    );
                })
        );
    });

    it('Open phone preview', function () {
        return (
            this.browser
                .url(`${baseUrl}phone.hbs`)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options, done) {
                            window.postMessage(
                                JSON.stringify({
                                    action: 'appendremote',
                                    resource: options.phoneResource,
                                    id: 'form-selector',
                                    inline: true,
                                    appVersion: '1',
                                    lang: 'ru',
                                    fileId: 'phone',
                                    data: '*',
                                }),
                                '*',
                            );
                            done();
                        },
                    }),
                )
                // запрос за ресурсом
                .execute(function () {
                    return Array.prototype.slice
                        .call(document.getElementsByTagName('script'))
                        .map((item) => item.src);
                })
                .then(({ value: scripts }) => {
                    chai.expect(
                        scripts.filter(
                            (src) => src === `${resourceBaseUrl}phone_ru.js`,
                        ).length,
                    ).to.eq(1, 'can not find script request');
                })
                // hide phones
                .executeAsync((done) => {
                    const phone = document.getElementById('phone');
                    const previousLen = phone.children.length;
                    window.Ya._metrika._u.phone.hidePhones();
                    setTimeout(() => {
                        done([previousLen, phone.children.length]);
                    }, 500);
                })
                .then(({ value: [previous, current] }) => {
                    chai.expect(previous).to.be.eq(0);
                    // проверяем, что внутри появилась какая-то верстка
                    chai.expect(current).to.be.greaterThan(
                        0,
                        'should replace second phone',
                    );
                })
        );
    });
});
