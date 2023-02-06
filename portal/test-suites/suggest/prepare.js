'use strict';


const anyVal = '..*';

/**
 * @param {{param1: string, param2: string, param3: string}} input
 * @returns {RegExp}
 */
const isCorrectSuggestReq = ({
    param1 = anyVal, // .not_used, suggest, keyboard, mouse
    param2 = anyVal, //.p0, .p1, ...
    param3 = anyVal // click_by_mouse, button_by_mouse, keyboard
}) => new RegExp(
    `https?://yandex\\.ru/clck/jclck/.*${'\\' + param1}${'\\' + param2}${'\\' + anyVal}${'\\' + param3}`
);

const input = '//input[@id=\'text\' or contains(@class, \'mini-suggest__input\')]';
const button = 'Click .mini-suggest__button';
const suggest = (str) => 'Click //div[contains(@class, \'mini-suggest__popup_visible\')]' +
    `//ul[contains(@class, 'mini-suggest__popup-content')]//li[${str || ''}]`;
const tpah = (nth) => suggest(`@data-type='tpah'${nth ? ` and position()=${nth}` : ''}`);
const nav = (nth) => suggest(`@data-type='nav'${nth ? ` and position()=${nth}` : ''}`);

/**
 * @callback Validator
 * @param {string} pVal
 * @returns {{param1?: string, param2?: string: param3?: string}}
 */

/**
 * @param {(string | string[])[]} description
 * @param {Validator} validator
 */
function prepareTests(description, validator) {
    for (const [name, desc] of Object.entries(description)) {
        it(name, async function () {
            let [param, searchStr, searchWays] = desc;

            await this.browser
                .yaOpenMorda({
                    expectations: {
                        ignoreErrorsSource: /(console-api)|(network)/
                    }
                });
            const elem = await this.browser.$(input);
            await elem.waitForDisplayed();
            await elem.setValue(searchStr);

            await this.browser
                .execute(delaySubmit);

            if (!Array.isArray(searchWays)) {
                searchWays = [searchWays];
            }
            // Чтобы саджест точно прогрузился
            elem.click();
            await this.browser.$('.mini-suggest__item:nth-child(1)').then(elem => elem.waitForDisplayed());

            for (let searchWay of searchWays) {
                if (typeof searchWay === 'string' && searchWay.startsWith('Click ')) {
                    const sel = searchWay.slice(6);
                    await this.browser.$(sel).then(elem => elem.waitForDisplayed());
                    await this.browser.pause(500);
                    await this.browser.$(sel).then(elem => elem.click());
                } else if (searchWay === 'InputChange') {
                    await this.browser.waitUntil(
                        () => {
                            return this.browser.execute((val) => {
                                const node = $('#text, .mini-suggest__input')[0];
                                if (node) {
                                    return node.value && node.value !== val;
                                }
                                return false;
                            }, searchStr);
                        },
                        {
                            timeout: 5000,
                            timeoutMsg: 'Нет элемента ввода или его значение не изменялось в течение 5s'
                        }
                    );
                } else {
                    await this.browser.keys(searchWay);
                }
            }

            await this.browser.yaResourceRequested(isCorrectSuggestReq(validator(param)), {
                timeout: 500,
                timeoutMsg: `Не был запрошен suggest с параметром ${param}`
            });
        });
    }
}

function delaySubmit() {
    // Отличается для мобильной и пк версий
    const form = document.querySelector('.search2, .search3');
    form && form.addEventListener('submit', e => {
        e.preventDefault();
        setTimeout(() => {
            form && form.submit();
        }, 10000);
    });
}

module.exports = {
    input, button, nav, tpah, suggest,
    prepareTests
};
