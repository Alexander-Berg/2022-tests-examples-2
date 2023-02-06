'use strict';


specs('touch', function () {
    const {button, nav, tpah, prepareTests} = require('./prepare');

    describe('Саджест. Счетчики редирлога. Тип взаимодействия пользователя с саджестом (emulation)', function () {
        const description = {
            'Проверка параметра not_used': ['.not_used', 'котик', 'Enter'],
            // Иногда tpah может не нажиматься без клика на поисковую строку
            'Проверка параметра tpah': ['.tpah', 'котик', [tpah(1), 'InputChange', 'Enter']],
            'Проверка параметра mouse': ['.mouse', 'янд', [tpah(1), nav()]]
        };
        prepareTests(description, pVal => ({param1: pVal}));
    });

    describe('Саджест. Счетчики редирлога. Номер подсказки (emulation)', function () {
        const description = {
            'Проверка параметра p0 с тапахедом': ['.p0', 'котик', [tpah(1), button]],
            'Проверка параметра p0 без саджеста': ['.p0', 'котик', button]
        };
        prepareTests(description, pVal => ({param2: pVal}));
    });

    describe('Саджест. Счетчики редирлога. Способы отправки запроса (emulation)', function () {
        const description = {
            // Ошибка в описании теста click_by_mouse на TestPalm
            'Проверка параметра button_by_mouse при нажатии на тапахэд': [
                '.button_by_mouse', 'котик', [tpah(1), button]
            ],
            'Проверка параметра button_by_mouse': ['.button_by_mouse', 'котик', button]
        };
        prepareTests(description, pVal => ({param3: pVal}));
    });
});
