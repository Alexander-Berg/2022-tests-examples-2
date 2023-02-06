import makeDataTestIdSelector from 'tests/e2e/utils/make-data-test-id-selector';

/**
 * @constant
 * @description Время ожидания
 */
const DEFAULT_WAIT_TIME = 2500;

type WaitForExistOptions = Exclude<Parameters<WebdriverIO.Element['waitForEnabled']>[0], undefined>;
type Options = Partial<Omit<WaitForExistOptions, 'reverse'>>;
type WaitUntilOptions = Exclude<Parameters<WebdriverIO.Element['waitUntil']>[1], undefined>;

/**
 * @function
 * @description Аналогично `element.waitForEnabled({reverse: false})`
 * @param page
 * @param selector
 * @param options
 */
export async function waitForTestIdSelectorEnabled(
    this: WebdriverIO.Browser,
    selector: Hermione.Selector,
    options?: Options
) {
    const element = await this.$(makeDataTestIdSelector(selector));
    await element.waitForEnabled({timeout: DEFAULT_WAIT_TIME, ...options, reverse: false});
}

/**
 * @function
 * @description Аналогично `element.waitForEnabled({reverse: true})`
 * @param page
 * @param selector
 * @param options
 */
export async function waitForTestIdSelectorDisabled(
    this: WebdriverIO.Browser,
    selector: Hermione.Selector,
    options?: Options
) {
    const element = await this.$(makeDataTestIdSelector(selector));
    await element.waitForEnabled({timeout: DEFAULT_WAIT_TIME, ...options, reverse: true});
}

export async function waitForTestIdSelectorAriaDisabled(
    this: WebdriverIO.Browser,
    selector: Hermione.Selector,
    options?: WaitUntilOptions
) {
    const testIdSelector = makeDataTestIdSelector(selector);
    const attributeName = 'aria-disabled';

    const opts = {
        timeout: DEFAULT_WAIT_TIME,
        ...options
    };
    opts.timeoutMsg = `element ("${testIdSelector}") still not has ${attributeName}='true' after ${opts.timeout}ms`;

    const element = this.$(testIdSelector);
    await element.waitUntil(async function () {
        return (await element.getAttribute(attributeName)) === 'true';
    }, opts);
}

export async function waitForTestIdSelectorAriaEnabled(
    this: WebdriverIO.Browser,
    selector: Hermione.Selector,
    options?: WaitUntilOptions
) {
    const testIdSelector = makeDataTestIdSelector(selector);
    const attributeName = 'aria-disabled';

    const opts = {
        timeout: DEFAULT_WAIT_TIME,
        ...options
    };

    opts.timeoutMsg = `element "${testIdSelector}" still not has ${attributeName}='false' after ${opts.timeout}ms`;

    const element = this.$(testIdSelector);
    await element.waitUntil(async function () {
        return (await element.getAttribute(attributeName)) === 'false';
    }, opts);
}

export async function waitForTestIdSelectorAriaChecked(
    this: WebdriverIO.Browser,
    selector: Hermione.Selector,
    options?: WaitUntilOptions
) {
    const testIdSelector = makeDataTestIdSelector(selector);
    const attributeName = 'aria-checked';

    const opts = {
        timeout: DEFAULT_WAIT_TIME,
        ...options
    };
    opts.timeoutMsg = `element ("${testIdSelector}") still not has ${attributeName}='true' after ${opts.timeout}ms`;

    const element = this.$(testIdSelector);
    await element.waitUntil(async function () {
        return (await element.getAttribute(attributeName)) === 'true';
    }, opts);
}

export async function waitForTestIdSelectorAriaNotChecked(
    this: WebdriverIO.Browser,
    selector: Hermione.Selector,
    options?: WaitUntilOptions
) {
    const testIdSelector = makeDataTestIdSelector(selector);
    const attributeName = 'aria-checked';

    const opts = {
        timeout: DEFAULT_WAIT_TIME,
        ...options
    };
    opts.timeoutMsg = `element ("${testIdSelector}") still not has ${attributeName}='false' after ${opts.timeout}ms`;

    const element = this.$(testIdSelector);
    await element.waitUntil(async function () {
        return (await element.getAttribute(attributeName)) === 'false';
    }, opts);
}

export async function waitForTestIdSelectorClickable(
    this: WebdriverIO.Browser,
    selector: Hermione.Selector,
    options?: WaitUntilOptions
) {
    const testIdSelector = makeDataTestIdSelector(selector);
    const opts = {
        timeout: DEFAULT_WAIT_TIME,
        ...options
    };

    const element = this.$(testIdSelector);
    await element.waitForClickable({
        timeout: opts.timeout,
        timeoutMsg: `Element has not become clickable in ${opts.timeout}ms`
    });
}

export async function waitForTestIdSelectorNotClickable(
    this: WebdriverIO.Browser,
    selector: Hermione.Selector,
    options?: WaitUntilOptions
) {
    const testIdSelector = makeDataTestIdSelector(selector);
    const opts = {
        timeout: DEFAULT_WAIT_TIME,
        ...options
    };

    const element = this.$(testIdSelector);
    await element.waitForClickable({
        timeout: opts.timeout,
        timeoutMsg: `Element has not become clickable in ${opts.timeout}ms`,
        reverse: true
    });
}

export async function waitForTestIdSelectorReadyToPlayVideo(
    this: WebdriverIO.Browser,
    selector: Hermione.Selector,
    options?: WaitUntilOptions
) {
    const testIdSelector = makeDataTestIdSelector(selector);
    const propertyName = 'readyState';

    const opts = {
        timeout: DEFAULT_WAIT_TIME * 2,
        ...options
    };
    opts.timeoutMsg = `element ("${testIdSelector}") still not has ${propertyName}='4' after ${opts.timeout}ms`;

    const element = this.$(testIdSelector);
    await element.waitUntil(async function () {
        return (await element.getProperty(propertyName)) === 4;
    }, opts);
}

export type WaitForTestIdSelectorEnabled = typeof waitForTestIdSelectorEnabled;
export type WaitForTestIdSelectorDisabled = typeof waitForTestIdSelectorDisabled;
export type WaitForTestIdSelectorAriaDisabled = typeof waitForTestIdSelectorAriaDisabled;
export type WaitForTestIdSelectorAriaEnabled = typeof waitForTestIdSelectorAriaEnabled;
export type WaitForTestIdSelectorAriaChecked = typeof waitForTestIdSelectorAriaChecked;
export type WaitForTestIdSelectorAriaNotChecked = typeof waitForTestIdSelectorAriaNotChecked;
export type WaitForTestIdSelectorClickable = typeof waitForTestIdSelectorClickable;
export type WaitForTestIdSelectorNotClickable = typeof waitForTestIdSelectorNotClickable;
export type WaitForTestIdSelectorReadyToPlayVideo = typeof waitForTestIdSelectorReadyToPlayVideo;
