import {makeDataTestIdSelector} from 'tests/e2e/utils/make-data-test-id-selector';

/**
 * @constant
 * @description Время ожидания
 */
const DEFAULT_WAIT_TIME = 15000;

/**
 * @constant
 * @description Время (задержка) перед запросом за элементом для компенсации временных лагов при рендеринге
 */
const DEFAULT_DELAY_TIME = 50;

type WaitForDisplayedOptions = Exclude<Parameters<WebdriverIO.Element['waitForDisplayed']>[0], undefined>;
type Options = WaitForDisplayedOptions & {delay?: number};

/**
 * @function
 * @description Ожидать пока элемент станет видимым
 * @param this
 * @param selector
 * @param options
 */
export async function waitForTestIdSelectorDisplayed(
    this: WebdriverIO.Browser,
    selector: Hermione.GenericSelector,
    options?: Options
) {
    await this.pause(options?.delay ?? DEFAULT_DELAY_TIME);
    const element = await this.$(makeDataTestIdSelector(selector));
    await element.waitForDisplayed({timeout: DEFAULT_WAIT_TIME, ...options});
}

export type WaitForTestIdSelectorDisplayed = typeof waitForTestIdSelectorDisplayed;
