import {parentPort} from 'worker_threads';

import {CRON_FINISHED} from '../types';

void (function () {
    const promise = new Promise<void>((resolve) => {
        setTimeout(() => {
            resolve();
        }, 1_000);
    });

    return promise.then(() => parentPort?.postMessage(CRON_FINISHED));
})();
