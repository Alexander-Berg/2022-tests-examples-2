import {makeDataTestIdSelector} from 'tests/e2e/utils/make-data-test-id-selector';

/**
 * @constant
 * @description Время ожидания на появление элемента в DOM дереве (чтобы нивелировать анимации и прочее)
 */
const DEFAULT_WAIT_TIME = 3500;

/**
 * @function
 * @description Ждем появления элемента в DOM дереве, после чего запрашивает его и возвращает
 * @param browser
 * @param genericSelector
 * @returns ElementHandle
 */
export async function assertBySelector(this: WebdriverIO.Browser, genericSelector: Hermione.GenericSelector) {
    const selector = makeDataTestIdSelector(genericSelector);
    const element = await this.$(selector);
    await element.waitForExist({timeout: DEFAULT_WAIT_TIME});
    return element;
}

export type AssertBySelector = typeof assertBySelector;
