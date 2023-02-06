import {HookFunctions} from '@wdio/types/build/Services';

type OnPrepareStartArgs = Parameters<Required<HookFunctions>['onPrepare']>;

/**
 * Gets executed once before all workers get launched.
 */
export function onPrepare(..._args: OnPrepareStartArgs) {
    // TODO
}
