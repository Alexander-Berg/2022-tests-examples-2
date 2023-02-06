import {makeDataTestIdSelector} from 'tests/e2e/utils/make-data-test-id-selector';

/**
 * @function
 * @description Скрытие элемента по testId и по селектору
 * @param browser
 * @param selector
 */
export async function hideBySelector(this: WebdriverIO.Browser, selector: Hermione.GenericSelector) {
    const elementSelector = makeDataTestIdSelector(selector);

    return this.execute((selector) => {
        const element = document.querySelector<HTMLElement>(selector);

        if (element) {
            element.style.display = 'none';
        }
    }, elementSelector);
}

export type HideBySelector = typeof hideBySelector;
