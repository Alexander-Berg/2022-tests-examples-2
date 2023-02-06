import {AwsClient} from '@lavka-js-toolbox/s3-provider';
import {existsSync, PathLike, promises as fs, unlinkSync} from 'fs';
import {join as joinPath} from 'path';

import type {LogWriter} from './types';
import {LoadTestingOptions} from './types';

export function createFileLogWriter(filepath: PathLike): LogWriter {
    return (message) => {
        void fs.appendFile(filepath, message + '\n');
    };
}

export function pMap<T, R>(
    iterable: T[],
    mapper: (it: T, index: number, total: number) => Promise<R>,
    {concurrency = Number.MAX_SAFE_INTEGER}: {concurrency?: number} = {}
) {
    return new Promise<R[]>((resolve, reject) => {
        const total = iterable.length;
        let index = 0;
        let resolved = 0;
        const results: R[] = [];

        if (!total) {
            return resolve(results);
        }

        const next = (): undefined | Promise<void> => {
            if (resolved >= total) {
                resolve(results);
                return;
            }

            if (index >= total) {
                return;
            }

            const ix = index;
            index++;

            return mapper(iterable[ix], ix, total)
                .then((result) => {
                    resolved++;
                    results[ix] = result;

                    return next();
                })
                .catch(reject);
        };

        for (let i = 0; i < Math.min(iterable.length, concurrency); i++) {
            void next();
        }
    });
}

export function getAwsClient({host, bucket, key, secret}: LoadTestingOptions['awsClient']) {
    return new AwsClient({host, bucket, key, secret});
}

export async function flushAwsRecordings(options: LoadTestingOptions, {concurrency = 10} = {}) {
    if (!options.awsClient.enabled) {
        return console.error('Aws disabled');
    }

    const client = getAwsClient(options.awsClient);
    const dir = joinPath(options.artifactsDir, options.recordingName);
    const queue: {key: string; file: string}[] = [];

    for await (const {
        item: {key}
    } of client.listObjects({prefix: options.awsClient.prefix + '/', timeout: options.awsClient.timeout})) {
        const file = key.split('/').pop();
        if (!file) {
            throw new Error(`Invalid AWS object key: "${key}"`);
        }
        queue.push({key, file});
    }

    if (queue.length) {
        await pMap(
            queue,
            async ({key, file}, index, total) => {
                console.log(`Removing [${index + 1}/${total}] ${file}`);
                await client.dropObject({key, timeout: options.awsClient.timeout});
                const filePath = joinPath(dir, file);
                if (existsSync(filePath)) {
                    unlinkSync(filePath);
                }
            },
            {concurrency}
        );
    } else {
        console.log('No AWS objects found');
    }
}
