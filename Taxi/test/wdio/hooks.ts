import {Hooks} from '@wdio/types/build/Services';

import {onPrepare, onWorkerEnd, onWorkerStart, afterTest} from '../utils/wdio-hooks';

// =====
// Hooks
// =====
// https://webdriver.io/docs/configurationfile/
export const hooksConfig: Hooks = {
    afterTest,
    onPrepare,
    onWorkerEnd,
    onWorkerStart,
};
