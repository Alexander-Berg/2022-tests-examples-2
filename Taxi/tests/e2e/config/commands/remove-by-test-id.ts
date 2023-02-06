import {makeDataTestIdSelector} from 'tests/e2e/utils/make-data-test-id-selector';

/**
 * @function
 * @description Удаление элемента из DOM-дерева по testId
 * @param browser
 * @param testId
 * @returns ElementHandle
 */
export async function removeByTestId(this: WebdriverIO.Browser, testId: string) {
    const selector = makeDataTestIdSelector(testId);

    return this.execute((selector) => {
        const element = document.querySelector(selector);

        if (element) {
            element.remove();
        }
    }, selector);
}

export type RemoveByTestId = typeof removeByTestId;
