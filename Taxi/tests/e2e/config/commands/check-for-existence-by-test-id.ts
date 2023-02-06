import {makeDataTestIdSelector} from 'tests/e2e/utils/make-data-test-id-selector';

/**
 * @function
 * @description Проверка на существование элемента по testId
 * @param browser
 * @param selector
 * @returns Boolean
 */
export async function checkForExistenceByTestId(this: WebdriverIO.Browser, selector: Hermione.GenericSelector) {
    const dataTestIdSelector = makeDataTestIdSelector(selector);
    const element = await this.$(dataTestIdSelector);

    return await element.isExisting();
}

export type CheckForExistenceByTestId = typeof checkForExistenceByTestId;
