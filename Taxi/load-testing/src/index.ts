/**
 * Данный файл не должен импортировать ничего лишнего,
 * основной импорт должен быть внутри метода `initLoadTesting`
 */

import assert from 'assert';
import {existsSync} from 'fs';
import {get as getByPath, merge} from 'lodash';

import type {EnabledLoadTesting, LoadTesting, LoadTestingOptions} from './types';

const STATUS = {
    DISABLED: 'disabled',
    ENABLED: 'enabled'
} as const;

export * from './types';
export * from './util';

export const loadTesting: LoadTesting = {status: STATUS.DISABLED};

export async function initLoadTesting(enabled: boolean, options: Partial<LoadTestingOptions>) {
    if (!enabled) {
        return;
    }

    const {createApi} = await import('./api');

    const defaults: LoadTestingOptions = {
        logLevel: 'ERROR',
        logsFile: '',
        artifactsDir: 'load-testing',
        recordingName: 'load-testing',
        headFile: 'index.json',
        persistInterval: 10,
        persistThreshold: 10,
        polly: {
            logging: false
        },
        awsClient: {
            enabled: false,
            host: '',
            bucket: '',
            key: '',
            secret: '',
            prefix: 'load-testing',
            timeout: 10000,
            concurrency: 10
        }
    };

    const apiOptions = merge(defaults, options);

    ['artifactsDir', 'recordingName'].forEach((dotPath) => {
        assert(getByPath(apiOptions, dotPath), `Missed mandatory "${dotPath}" option`);
    });

    const api = await createApi(apiOptions);

    if (!existsSync(api.options.artifactsDir)) {
        throw new Error(`Recordings directory does not exist: "${api.options.artifactsDir}"`);
    }

    Object.assign(loadTesting, {status: STATUS.ENABLED, api});

    api.log.info(`Initialized load-testing :: log level "${options.logLevel}"`);
}

export function isLoadTestingEnabled(loadTesting: LoadTesting): loadTesting is EnabledLoadTesting {
    return loadTesting.status === STATUS.ENABLED;
}
