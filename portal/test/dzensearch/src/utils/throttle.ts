/* eslint-disable */

import {AnyFunction, debounce, DebounceReturnType, Options} from './debounce';

const defaultOptions = {
    leading: true,
    trailing: true,
};

/**
 * Это копия throttle из lodash
 * @see https://github.com/lodash/lodash/blob/master/throttle.js
 */
export const throttle = <F extends AnyFunction>(
    func: F,
    wait = 0,
    options: Partial<Options> = defaultOptions,
): DebounceReturnType<F> => {
    const {leading = defaultOptions.leading, trailing = defaultOptions.trailing} = options;

    return debounce(func, wait, {
        leading,
        trailing,
        maxWait: wait,
    });
};
