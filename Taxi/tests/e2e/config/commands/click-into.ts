import {patchStyles} from 'tests/e2e/config/util';

type ClickOptions = Exclude<Parameters<WebdriverIO.Element['click']>[0], undefined>;
type WaitOptions = {waitNavigation?: boolean; waitRender?: boolean; waitForClickable?: boolean};
type CustomOptions = {hoverBeforeClick?: boolean};

export type ClickIntoOptions = Partial<WaitOptions & ClickOptions & CustomOptions>;

const NAVIGATION_TIMEOUT = 10000;
const WAIT_FOR_CLICKABLE_TIMEOUT = 30000;
const WAIT_AFTER_HOVER_TIMEOUT = 300;

/**
 * @function
 * @description Находит элемент по data-testid селектору и кликает в него
 */
export async function clickInto(
    this: WebdriverIO.Browser,
    selector: Hermione.GenericSelector,
    options?: ClickIntoOptions
) {
    const {waitNavigation, waitRender, waitForClickable, hoverBeforeClick, ...restOptions} = options || {};

    const element = await this.assertBySelector(selector);

    if (waitForClickable) {
        await element.waitForClickable({
            timeout: WAIT_FOR_CLICKABLE_TIMEOUT,
            timeoutMsg: `Element has not become clickable in ${WAIT_FOR_CLICKABLE_TIMEOUT}ms`
        });
    }

    if (hoverBeforeClick) {
        await element.moveTo();
        await this.pause(WAIT_AFTER_HOVER_TIMEOUT);
    }

    const promises = [];

    if (waitNavigation) {
        const previousUrl = await this.getUrl();
        const navigationPromise = this.waitUntil(async () => (await this.getUrl()) !== previousUrl, {
            timeout: NAVIGATION_TIMEOUT,
            interval: Math.floor(NAVIGATION_TIMEOUT / 5),
            timeoutMsg: `There was no navigation in ${NAVIGATION_TIMEOUT}ms`
        });
        promises.push(navigationPromise);
    }

    promises.push(element.click(restOptions));
    await Promise.all(promises);

    if (waitRender) {
        await this.waitUntilRendered();
        if (waitNavigation) {
            await this.execute(patchStyles);
        }
    }
}

/**
 * @function
 * @description Вызывает clickInto с параметрами {waitRender: true, waitForClickable: true}
 */
export async function clickIntoEnsured(
    this: WebdriverIO.Browser,
    selector: Hermione.GenericSelector,
    options?: Omit<ClickIntoOptions, 'waitRender' | 'waitForClickable'>
) {
    return this.clickInto(selector, {...options, waitRender: true, waitForClickable: true});
}

export type ClickInto = typeof clickInto;
export type ClickIntoEnsured = typeof clickIntoEnsured;
