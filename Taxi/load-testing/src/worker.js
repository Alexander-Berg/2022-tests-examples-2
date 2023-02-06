/**
 * Успешное завершение обработчика должно возвращать строковое сообщение
 */

const {isMainThread, parentPort, workerData} = require('worker_threads');
const {writeFileSync} = require('fs');
const {join: joinPath} = require('path');
const {AwsClient} = require('@lavka-js-toolbox/s3-provider');

const api = {
    PERSIST_RECORDINGS: async (payload, options) => {
        let totalFiles = 0;
        let bytes = 0;

        if (payload && Array.isArray(payload) && payload.length) {
            const dir = joinPath(options.artifactsDir, options.recordingName);
            totalFiles = payload.length;

            for (const it of payload) {
                writeFileSync(joinPath(dir, it.name), it.content, {encoding: 'utf8'});
                bytes += it.content.length;
            }

            if (options.awsClient.enabled) {
                const client = new AwsClient({
                    host: options.awsClient.host,
                    bucket: options.awsClient.bucket,
                    key: options.awsClient.key,
                    secret: options.awsClient.secret
                });

                for (const it of payload) {
                    const key = [options.awsClient.prefix, it.name].join('/');
                    await client.uploadObject({key, content: it.content});
                }
            }
        }

        return `persisted ${totalFiles} files (${(bytes / 1024 / 1024).toFixed(2)} mb)`;
    }
};

if (!isMainThread) {
    handle();
}

function handle() {
    if (!workerData) {
        throw new Error('Empty worker data');
    }

    const {action, payload, options} = workerData;

    if (action in api) {
        const result = api[action](payload, options);

        if (result instanceof Promise) {
            return result.then((message) => resolve(message)).catch((e) => resolve(e));
        }

        return resolve(result);
    } else {
        return resolve(new Error(`Invalid worker action: "${action}"`));
    }
}

function resolve(message) {
    if (!parentPort) {
        throw new Error('Broken worker parent port');
    }

    parentPort.postMessage(message);
    process.exit();
}
