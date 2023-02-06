import { Browser } from 'hermione';
import { Options } from '../utils';

const customWaitForEnabled: Browser['customWaitForEnabled'] = function(
    this: Browser,
    options: Options<Browser['customWaitForEnabled']> = {},
) {
    const { selector, milliseconds = 30000, reverse = false } = options;

    return this.waitUntil(async () => {
        const disabled = await this.customIsElementDisabled(selector);
        return disabled === reverse;
    }, milliseconds);
};

export { customWaitForEnabled };
