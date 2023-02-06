import makeDataTestIdSelector from 'tests/e2e/utils/make-data-test-id-selector';

/**
 * @constant
 * @description Время ожидания на появление элемента в DOM дереве (чтобы нивелировать анимации и прочее)
 */
const DEFAULT_WAIT_TIME = 2500;

/**
 * @function
 * @description Ждем появления элемента в DOM дереве, после чего запрашивает его и возвращает
 * @param browser
 * @param selector
 * @returns ElementHandle
 */
export default async function findByTestId(this: WebdriverIO.Browser, selector: Hermione.Selector) {
    const dataTestIdSelector = makeDataTestIdSelector(selector);
    const element = await this.$(dataTestIdSelector);
    await element.waitForExist({timeout: DEFAULT_WAIT_TIME});
    return element;
}

export type FindByTestId = typeof findByTestId;
