import {parentPort} from 'worker_threads';

void (function () {
    const promise = new Promise<void>((resolve) => {
        setTimeout(() => {
            resolve();
        }, 10_000);
    });

    return promise.catch((error) => parentPort?.postMessage(error));
})();
