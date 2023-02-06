import {isPlainObject, snakeCase} from 'lodash';
import slugify from 'slugify';
import makeDataTestIdSelector from 'tests/e2e/utils/make-data-test-id-selector';

type Options = Hermione.AssertViewOpts & {
    snapshotName?: string;
    attempts?: number;
    removeShadows?: boolean;
    stretch?: boolean;
};
type CssObject = {property: string; value: null | string; priority: string | undefined};

const DEFAULT_SELECTOR = 'body';
const DEFAULT_ATTEMPTS_COUNT = 3;

const counters = new Map<string, number>();

function getSnapshotIdentifier(browser: WebdriverIO.Browser, snapshotName?: string) {
    const testUuid = browser.executionContext.uuid;
    const testName = browser.executionContext.title;

    const counter = (counters.get(testUuid) || 0) + 1;
    counters.set(testUuid, counter);

    const suffix = snapshotName ? snapshotName : counter;

    return slugify([testName, suffix].map((value) => snakeCase(String(value))).join('_'));
}

async function assertImage(this: WebdriverIO.Browser, options?: Options): Promise<void>;
async function assertImage(this: WebdriverIO.Browser, selector: Hermione.Selector, options?: Options): Promise<void>;
async function assertImage(
    this: WebdriverIO.Browser,
    selectorOrOptions?: Hermione.Selector | Options,
    options?: Options
) {
    let assertOptions: Options | undefined;
    let selector: string;

    if (isSelector(selectorOrOptions)) {
        selector = makeDataTestIdSelector(selectorOrOptions);
        assertOptions = options;
    } else if (isOptions(selectorOrOptions)) {
        options = selectorOrOptions;
        selector = DEFAULT_SELECTOR;
    } else {
        selector = DEFAULT_SELECTOR;
    }

    const snapShotName = getSnapshotIdentifier(this, options?.snapshotName);

    const performScreenshot = async (count: number): Promise<void> => {
        const cancelers: Array<() => unknown | Promise<unknown>> = [];

        if (options?.removeShadows) {
            const restore = await this.execute(changeCss, selector, {
                property: 'box-shadow',
                value: 'none',
                priority: 'important'
            });
            cancelers.push(() => this.execute(changeCss, selector, restore));
        }

        if (options?.stretch) {
            const initialSize = await this.getWindowSize();
            await this.setWindowSize(initialSize.width, 9999);
            const restore = await this.execute(changeCss, selector, {
                property: 'height',
                value: 'auto',
                priority: 'important'
            });
            cancelers.push(() =>
                Promise.all([
                    this.setWindowSize(initialSize.width, initialSize.height),
                    this.execute(changeCss, selector, restore)
                ])
            );
        }

        await this.assertView(snapShotName, selector, assertOptions);

        if (cancelers.length > 0) {
            await Promise.all(cancelers.map((cancel) => cancel()));
        }

        const assertViewResults = this.executionContext.hermioneCtx.assertViewResults;
        if (assertViewResults) {
            const error = assertViewResults._results.find((it) => it instanceof Error && it.stateName === snapShotName);
            if (error && count > 0) {
                assertViewResults._results = assertViewResults._results.filter((it) => it !== error);
                return performScreenshot(count - 1);
            }
        }
    };

    await performScreenshot(options?.attempts ?? DEFAULT_ATTEMPTS_COUNT);
}

function isSelector(value: unknown): value is Hermione.Selector {
    return Boolean(value) && (typeof value === 'string' || Array.isArray(value));
}

function isOptions(value: unknown): value is Options {
    return isPlainObject(value);
}

function changeCss(selector: string, css: CssObject) {
    const element = document.querySelector(selector);
    const restore: CssObject = {property: css.property, value: null, priority: undefined};
    if (element instanceof HTMLElement) {
        restore.value = element.style.getPropertyValue(css.property);
        restore.priority = element.style.getPropertyPriority(css.property);
        element.style.setProperty(css.property, css.value, css.priority);
    }
    return restore;
}

export default assertImage;

export type AssertImage = typeof assertImage;
