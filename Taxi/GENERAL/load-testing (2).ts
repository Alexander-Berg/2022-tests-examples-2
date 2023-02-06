import type {LoadTestingOptions} from '@lavka-js-toolbox/load-testing';
import {join as joinPath} from 'path';

import {serviceResolve} from '@/src/lib/resolve';

export const baseDir = serviceResolve('.load-testing');
const artifactsDir = joinPath(baseDir, 'files');
const recordingName = 'lavka-pigeon-market.v1';

export const loadTestingConfig = {
    artifactsDir,
    recordingName,
    logLevel: process.env.LOAD_TESTING_LOG_LEVEL ?? 'INFO',
    logsFile: joinPath(baseDir, 'load-testing.log'),
    awsClient: {
        enabled: Boolean(process.env.AWS_BUCKET && process.env.AWS_KEY && process.env.AWS_SECRET),
        host: process.env.AWS_HOST || 's3.mds.yandex.net',
        bucket: process.env.AWS_BUCKET,
        key: process.env.AWS_KEY,
        secret: process.env.AWS_SECRET,
        prefix: ['load-testing', recordingName].join('/')
    }
} as LoadTestingOptions;
