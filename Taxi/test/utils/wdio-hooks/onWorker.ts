import {HookFunctions} from '@wdio/types/build/Services';

type OnWorkerStartArgs = Parameters<Required<HookFunctions>['onWorkerStart']>;

/**
 * Gets executed before a worker process is spawned and can be used to initialise specific service
 * for that worker as well as modify runtime environments in an async fashion.
 */
export function onWorkerStart(..._args: OnWorkerStartArgs) {
    // TODO
}

type OnWorkerEndArgs = Parameters<Required<HookFunctions>['onWorkerEnd']>;

/**
 * Gets executed just after a worker process has exited.
 */
export function onWorkerEnd(..._args: OnWorkerEndArgs) {
    // TODO
}
