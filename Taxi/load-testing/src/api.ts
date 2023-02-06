/* eslint-disable @typescript-eslint/no-explicit-any */

import {createWriteStream, existsSync, mkdirSync, readdirSync, readFileSync} from 'fs';
import {join as joinPath} from 'path';
import stream from 'stream';
import {promisify} from 'util';
import {Worker} from 'worker_threads';

import {ExpressProvider} from './express-provider';
import type {LoadTestingApi, LoadTestingOptions, LogWriter, PersistThresholdCallback} from './types';
import {createFileLogWriter, getAwsClient, pMap} from './util';

type ApiContainer = {
    persistData?: any;
    persistRequestIds: Set<string>;
    express?: ExpressProvider;
    persistTotal: number;
    persistThreshold: number;
    persistThresholdCallback?: PersistThresholdCallback;
};

type CreateWorker = {
    action: 'PERSIST_RECORDINGS';
    payload: any;
    options: LoadTestingOptions;
};

const LOG_LEVELS = {
    DEBUG: 0,
    INFO: 1,
    WARN: 2,
    ERROR: 3
} as const;

const WORKER_PATH = joinPath(__dirname, 'worker.js');

const pPipeline = promisify(stream.pipeline);

export async function createApi(options: LoadTestingOptions) {
    const container: ApiContainer = {
        persistRequestIds: new Set(),
        persistTotal: 0,
        persistThreshold: 0
    };
    const log = createLog({options});

    createRecordingsDir({options});
    await downloadRecordingsFromAws({options, log});

    const stringifyRecordings = (data: any) => JSON.stringify(data, null, 2);

    startPersistInterval({container, stringifyRecordings, options, log});

    const api: LoadTestingApi = {
        options,

        log,

        loadRecordingsCache() {
            const dir = joinPath(options.artifactsDir, options.recordingName);
            const headFile = joinPath(dir, options.headFile);

            if (!existsSync(headFile)) {
                return;
            }

            try {
                const parseFile = (file: string) => JSON.parse(readFileSync(file, {encoding: 'utf8'}));
                const data = parseFile(headFile);
                data.log.entries = [];

                readdirSync(dir).forEach((file) => {
                    try {
                        const entry = parseFile(joinPath(dir, file));
                        if (entry && entry._id) {
                            data.log.entries.push(entry);
                        }
                    } catch (e) {
                        log.error(`Read recording file error: ${String(e)}`);
                    }
                });

                log.info(`Read ${data.log.entries.length} recordings`);

                return data;
            } catch (e) {
                log.error(`Corrupted recordings volume: ${String(e)}`);
            }
        },

        stringifyRecordings,

        setPersistThresholdCallback(callback) {
            container.persistThresholdCallback = callback;
        },

        persistRecordings(data, newRequestIds) {
            container.persistData = data;
            newRequestIds.forEach((id) => container.persistRequestIds.add(id));
        },

        createExpressProvider: (app) => (container.express = new ExpressProvider(app)),

        express: () => {
            if (!container.express) {
                throw new Error('Express provider should be initialized first!');
            }

            return container.express;
        }
    };

    return api;
}

function createLog({options}: {options: LoadTestingOptions}) {
    const noop = () => {
        /* do nothing */
    };

    const logWriter = options.logsFile ? createFileLogWriter(options.logsFile) : noop;

    const createLogWriter = (level: LoadTestingOptions['logLevel']): LogWriter => {
        if (LOG_LEVELS[level] < LOG_LEVELS[options.logLevel]) {
            return noop;
        }

        return (message) => {
            logWriter(`[${new Date().toISOString()}][${level}] ${message}`);
        };
    };

    return {
        debug: createLogWriter('DEBUG'),
        info: createLogWriter('INFO'),
        warn: createLogWriter('WARN'),
        error: createLogWriter('ERROR')
    };
}

function createRecordingsDir({options}: {options: LoadTestingOptions}) {
    const dir = joinPath(options.artifactsDir, options.recordingName);
    if (!existsSync(dir)) {
        mkdirSync(dir);
    }
}

async function downloadRecordingsFromAws({options, log}: {options: LoadTestingOptions; log: LoadTestingApi['log']}) {
    if (!options.awsClient.enabled) {
        return log.error('Aws disabled');
    }

    const client = getAwsClient(options.awsClient);

    try {
        log.info('Collecting AWS objects');

        const keys: string[] = [];
        for await (const {
            item: {key}
        } of client.listObjects({prefix: options.awsClient.prefix + '/', timeout: options.awsClient.timeout})) {
            keys.push(key);
        }

        log.info(`Found ${keys.length} AWS objects`);

        await pMap(
            keys,
            async (key, index, total) => {
                log.info(`Downloading [${index + 1}/${total}] ${key}`);
                const readStream = client.getObjectStream({key, timeout: options.awsClient.timeout});
                const filename = key.split('/').pop();
                if (typeof filename === 'string') {
                    const writeStream = createWriteStream(
                        joinPath(options.artifactsDir, options.recordingName, filename)
                    );
                    await pPipeline(readStream, writeStream);
                }
            },
            {concurrency: options.awsClient.concurrency}
        );
    } catch (e) {
        log.error(`Recordings download error: ${String(e)}`);
    }
}

function startPersistInterval({
    container,
    stringifyRecordings,
    options,
    log
}: {
    container: ApiContainer;
    stringifyRecordings: LoadTestingApi['stringifyRecordings'];
    options: LoadTestingOptions;
    log: LoadTestingApi['log'];
}) {
    const dispatchThreshold = () => {
        if (container.persistThreshold >= options.persistThreshold) {
            container.persistThreshold -= options.persistThreshold;
            log.warn(`Persist threshold (${options.persistThreshold})`);
            if (container.persistThresholdCallback) {
                container.persistThresholdCallback(container.persistTotal);
            }
            dispatchThreshold();
        }
    };

    const countPersistPayload = (add: number) => {
        container.persistTotal += add;
        container.persistThreshold += add;
        dispatchThreshold();
    };

    setInterval(() => {
        const requestFilesCount = container.persistRequestIds.size;

        if (!container.persistData || !requestFilesCount) {
            return;
        }

        const files: {name: string; content: string}[] = [];
        const {
            log: {entries, ...rest}
        } = container.persistData;

        // Using fastest iteration style:
        for (let i = 0; i < entries.length; i++) {
            if (container.persistRequestIds.has(entries[i]._id)) {
                files.push({
                    name: entries[i]._id,
                    content: stringifyRecordings(entries[i])
                });
            }

            if (files.length >= requestFilesCount) {
                log.info(`Found ${requestFilesCount} recordings (${i + 1} iterations of ${entries.length})`);
                break;
            }
        }

        countPersistPayload(files.length);

        // Push head file at the end:
        files.push({
            name: options.headFile,
            content: stringifyRecordings({log: rest})
        });

        createWorker({action: 'PERSIST_RECORDINGS', payload: files, options})
            .then((msg) => log.info(`Recordings persisted: ${String(msg)}`))
            .catch((e) => log.error(`Persist recordings error: ${String(e)}`));

        container.persistData = undefined;
        container.persistRequestIds = new Set();
    }, options.persistInterval * 1000);
    log.info(`Recordings would be persisted every ${options.persistInterval}s`);
}

function createWorker({action, payload, options}: CreateWorker) {
    const worker = new Worker(WORKER_PATH, {workerData: {action, payload, options}});

    return new Promise((resolve, reject) => {
        worker.once('error', reject);
        worker.once('message', (data) => (data instanceof Error ? reject(data) : resolve(data)));
        worker.once('exit', () => reject(new Error('Something wrong!')));
    });
}
