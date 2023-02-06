import { Browser } from 'hermione';
import { Options } from '../utils';

const customWaitForRedirect: Browser['customWaitForRedirect'] = function(
    this: Browser,
    options: Options<Browser['customWaitForRedirect']> = {},
) {
    const {
        url: oldUrl,
        timeout = 30000,
        timeoutMsg = 'Redirect did not happen',
        interval = 500,
    } = options;

    if (typeof oldUrl === 'string') {
        return this.waitUntil(
            async () => {
                const url = await this.getUrl();

                return oldUrl !== url;
            },
            timeout,
            timeoutMsg,
            interval,
        );
    }

    return this.getUrl().then((oldUrl) => {
        return this.waitUntil(
            async () => {
                const url = await this.getUrl();

                return oldUrl !== url;
            },
            timeout,
            timeoutMsg,
            interval,
        );
    });
};

export { customWaitForRedirect };
