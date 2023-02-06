import {parentPort} from 'worker_threads';

void (function () {
    const promise = new Promise<void>((_, reject) => {
        setTimeout(() => {
            reject('some known error :)');
        }, 1_000);
    });

    return promise.catch((error) => parentPort?.postMessage(error));
})();
