/* eslint-disable */

export interface Options {
    leading: boolean;
    trailing: boolean;
    maxWait: number;
}

export type AnyFunction = (...args: any[]) => any;

const defaultOptions: Options = {
    leading: false,
    trailing: true,
    maxWait: 0,
};

export type DebounceReturnType<F extends AnyFunction> = {
    (...args: Parameters<F>): ReturnType<F>;
    cancel(): void;
    flush(): void;
};

/**
 * Это копия debounce из lodash
 * @see https://github.com/lodash/lodash/blob/master/debounce.js
 */
export const debounce = <F extends AnyFunction>(
    func: F,
    wait = 0,
    options: Partial<Options> = defaultOptions,
): DebounceReturnType<F> => {
    const {leading = defaultOptions.leading, trailing = defaultOptions.trailing} = options;
    const maxWait = Math.max(options.maxWait || defaultOptions.maxWait, wait);
    const maxing = Boolean(options.maxWait);
    let lastArgs: Parameters<F> | undefined;
    let lastThis: any;
    let result: ReturnType<F>;
    let timerId: ReturnType<typeof setTimeout> | undefined;
    let lastCallTime = 0;
    let lastInvokeTime = 0;

    const invokeFunc = (time: number): ReturnType<F> => {
        const args = lastArgs;
        const thisArg = lastThis;

        lastArgs = lastThis = undefined;
        lastInvokeTime = time;
        result = func.apply(thisArg, args || []);
        return result;
    };

    const leadingEdge = (time: number): ReturnType<F> => {
        // Reset any `maxWait` timer.
        lastInvokeTime = time;
        // Start the timer for the trailing edge.
        timerId = setTimeout(timerExpired, wait);
        // Invoke the leading edge.
        return leading ? invokeFunc(time) : result;
    };

    const remainingWait = (time: number): number => {
        const timeSinceLastCall = time - lastCallTime;
        const timeSinceLastInvoke = time - lastInvokeTime;
        const timeWaiting = wait - timeSinceLastCall;

        return options.maxWait ? Math.min(timeWaiting, maxWait - timeSinceLastInvoke) : timeWaiting;
    };

    const shouldInvoke = (time: number): boolean => {
        const timeSinceLastCall = time - lastCallTime;
        const timeSinceLastInvoke = time - lastInvokeTime;

        // Either this is the first call, activity has stopped and we're at the
        // trailing edge, the system time has gone backwards and we're treating
        // it as the trailing edge, or we've hit the `maxWait` limit.
        return (
            lastCallTime === 0 ||
            timeSinceLastCall >= wait ||
            timeSinceLastCall < 0 ||
            (maxing && timeSinceLastInvoke >= maxWait)
        );
    };

    const timerExpired = (): void => {
        const time = Date.now();
        if (shouldInvoke(time)) {
            return trailingEdge(time);
        }
        // Restart the timer.
        timerId = setTimeout(timerExpired, remainingWait(time));
    };

    const trailingEdge = (time: number): ReturnType<F> => {
        timerId = undefined;

        // Only invoke if we have `lastArgs` which means `func` has been
        // debounced at least once.
        if (trailing && lastArgs) {
            return invokeFunc(time);
        }
        lastArgs = lastThis = undefined;
        return result;
    };

    const cancel = (): void => {
        if (timerId !== undefined) {
            clearTimeout(timerId);
        }
        lastInvokeTime = 0;
        lastCallTime = 0;
        lastArgs = undefined;
        lastThis = undefined;
        timerId = undefined;
    };

    const flush = (): ReturnType<F> => (timerId === undefined ? result : trailingEdge(Date.now()));

    function debounced(...args: Parameters<F>): ReturnType<F> {
        const time = Date.now();
        const isInvoking = shouldInvoke(time);

        lastArgs = args;
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        lastThis = this;
        lastCallTime = time;

        if (isInvoking) {
            if (timerId === undefined) {
                return leadingEdge(lastCallTime);
            }
            if (maxing) {
                // Handle invocations in a tight loop.
                timerId = setTimeout(timerExpired, wait);
                return invokeFunc(lastCallTime);
            }
        }
        if (timerId === undefined) {
            timerId = setTimeout(timerExpired, wait);
        }
        return result;
    }
    debounced.cancel = cancel;
    debounced.flush = flush;
    return debounced;
};
