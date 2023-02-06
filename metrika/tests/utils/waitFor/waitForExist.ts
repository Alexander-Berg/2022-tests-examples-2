import { Browser } from 'hermione';
import { isUndefined } from 'lodash';
import { Options } from '../utils';

const customWaitForExist: Browser['customWaitForExist'] = function(
    this: Browser,
    options: Options<Browser['customWaitForExist']> = {},
) {
    const { reverse = false, milliseconds = 30000 } = options;
    let selector = options.selector;

    // при отсутствии селектора webdriverio кэширует результаты поиска элементов, если хотя бы один был найден.
    // Поэтому waitForExist не работате с флагом reverse.
    // Единственное теперь эта функция будет не правильно работать, если сценарий проверки будет появления элемента внутри другого.
    // Т.е теперь селектор всегда ищет по всему DOM
    let lastResult: any;
    if (isUndefined(selector)) {
        const lastPromise = this.lastPromise.inspect();
        selector = lastPromise.value.selector;

        lastResult = {
            ...lastPromise.value,
            value: [],
        };
    }

    return this.waitUntil(
        () => {
            this.lastResult = lastResult;
            return this.isExisting(selector).then<any>((exist) => {
                return exist === !reverse;
            }) as any;
        },
        milliseconds,
        `element ${selector} has not ${reverse ? 'dissapeared' : 'showed up'}`,
    );
};

export { customWaitForExist };
