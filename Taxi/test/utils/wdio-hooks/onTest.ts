import {HookFunctions} from '@wdio/types/build/Services';

type AfterTestStartArgs = Parameters<Required<HookFunctions>['afterTest']>;

/**
 * Function to be executed after a test (in Mocha/Jasmine only)
 */
export async function afterTest(...args: AfterTestStartArgs) {
    const [_test, _context, {passed}] = args;

    if (!passed) {
        await browser.takeScreenshot();
    }
}
