import {patchStyles} from 'tests/e2e/config/util';

type ClickOptions = Exclude<Parameters<WebdriverIO.Element['click']>[0], undefined>;
type WaitOptions = {waitNavigation?: boolean; waitRender?: boolean; waitForClickable?: boolean};
type Options = Partial<WaitOptions & ClickOptions>;

const NAVIGATION_TIMEOUT = 10000;
const WAIT_FOR_CLICKABLE_TIMEOUT = 30000;

/**
 * @function
 * @description Находит элемент по data-testid селектору и кликает в него
 */
export default async function clickInto(this: WebdriverIO.Browser, selector: Hermione.Selector, options?: Options) {
    const {waitNavigation, waitRender, waitForClickable, ...rest} = options || {};
    const element = await this.findByTestId(selector);

    if (waitForClickable) {
        await element.waitForClickable({
            timeout: WAIT_FOR_CLICKABLE_TIMEOUT,
            timeoutMsg: `Element has not become clickable in ${WAIT_FOR_CLICKABLE_TIMEOUT}ms`
        });
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

    promises.push(element.click(rest));
    await Promise.all(promises);

    if (waitRender) {
        await this.waitUntilRendered();
        if (waitNavigation) {
            await this.execute(patchStyles, {});
        }
    }
}

export type ClickInto = typeof clickInto;
