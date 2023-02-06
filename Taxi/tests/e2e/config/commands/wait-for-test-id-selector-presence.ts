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

type WaitForExistOptions = Exclude<Parameters<WebdriverIO.Element['waitForExist']>[0], undefined>;
type Options = Partial<Omit<WaitForExistOptions, 'reverse'>> & {delay?: number};

/**
 * @function
 * @description Аналогично `element.waitForExist({reverse: false})`
 * @param page
 * @param selector
 * @param options
 */
export async function waitForTestIdSelectorInDom(
    this: WebdriverIO.Browser,
    selector: Hermione.GenericSelector,
    options?: Options
) {
    await this.pause(options?.delay ?? DEFAULT_DELAY_TIME);
    const element = await this.$(makeDataTestIdSelector(selector));
    await element.waitForExist({timeout: DEFAULT_WAIT_TIME, ...options, reverse: false});
}

/**
 * @function
 * @description Аналогично `element.waitForExist({reverse: true})`
 * @param page
 * @param selector
 * @param options
 */
export async function waitForTestIdSelectorNotInDom(
    this: WebdriverIO.Browser,
    selector: Hermione.GenericSelector,
    options?: Options
) {
    await this.pause(options?.delay ?? DEFAULT_DELAY_TIME);
    const element = await this.$(makeDataTestIdSelector(selector));
    await element.waitForExist({timeout: DEFAULT_WAIT_TIME, ...options, reverse: true});
}

export type WaitForTestIdSelectorInDom = typeof waitForTestIdSelectorInDom;
export type WaitForTestIdSelectorNotInDom = typeof waitForTestIdSelectorNotInDom;
