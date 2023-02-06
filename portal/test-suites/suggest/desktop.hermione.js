'use strict';


specs('desktop', function() {
    describe('Проверка домена ручки саджеста', function () {
        const domainList = ['ru', 'com', 'ua', 'com.tr', 'uz'];
        for (let domain of domainList) {
            it(`Проверка ${domain} домена`, async function() {
                const isCorrectDomainReq = new RegExp(
                    // com.tr выдает true для com.tr и com_tr
                    // eslint-disable-next-line no-useless-escape
                    `https?://yandex\.${domain}/suggest/suggest-ya.cgi\?.*srv=morda_${domain}_desktop`
                );

                await this.browser.yaOpenMorda({
                    zone: domain,
                    getParams: {redirect: 0}
                });

                await this.browser.yaResourceRequested(isCorrectDomainReq, {
                    timeout: 500,
                    msg: `Домены в запросе не совпадают с доменом тестового стенда. ${domain}`
                });
            });
        }
    });

});

specs('desktop', function () {
    const {button, nav, suggest, prepareTests} = require('./prepare');

    describe('Счетчики редирлога. Тип взаимодействия пользователя с саджестом', function () {
        const description = {
            'Проверка параметра not_used': ['.not_used', 'котята', 'Enter'],
            'Проверка параметра suggest': ['.suggest', 'котята', ['ArrowDown', button]],
            'Проверка параметра keyboard': ['.keyboard', 'котята', ['ArrowDown', 'Enter']],
            'Проверка параметра mouse': ['.mouse', 'котята', ['Click #text', suggest(1)]],
            'Проверка параметра mouse и навигационной подсказки': [
                '.mouse', 'Яндекс', ['Click #text', nav()]
            ]
        };
        prepareTests(description, pVal => ({param1: pVal}));
    });

    describe('Счетчик редирлога. Номер подсказки', function () {
        const description = {
            'Проверка параметра p3': ['.p3', 'котята', suggest(3)],
            'Проверка параметра p0': ['.p0', 'котята', button]
        };
        prepareTests(description, pVal => ({param2: pVal}));
    });

    describe('Счетчики редирлога. Способы отправки запроса', function () {
        const description = {
            'Проверка параметра click_by_mouse': ['.click_by_mouse', 'котята', suggest(1)],
            'Проверка параметра button_by_mouse': ['.button_by_mouse', 'котята', button],
            'Проверка параметра keyboard': ['.keyboard', 'котята', 'Enter']
        };
        prepareTests(description, pVal => ({param3: pVal}));
    });
});
