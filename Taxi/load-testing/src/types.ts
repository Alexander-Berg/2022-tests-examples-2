/* eslint-disable @typescript-eslint/no-explicit-any */

import type {Headers, PollyServer, Request} from '@pollyjs/core';
import type {Express} from 'express';

export type LoadTestingOptions = {
    logLevel: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';
    logsFile: string;
    artifactsDir: string;
    recordingName: string;
    headFile: string;
    persistInterval: number; // seconds
    persistThreshold: number; // максимальное нормальное количество новых моков
    polly: {
        logging: boolean;
    };
    awsClient: {
        enabled: boolean;
        host: string;
        bucket: string;
        key: string;
        secret: string;
        prefix: string;
        timeout: number;
        concurrency: number;
    };
};

export type DisabledLoadTesting = {
    status: 'disabled';
};

export type EnabledLoadTesting = {
    status: 'enabled';
    api: LoadTestingApi;
};

export type LoadTesting = DisabledLoadTesting | EnabledLoadTesting;

export type PersistThresholdCallback = (total: number) => void;

export type LoadTestingApi = {
    options: LoadTestingOptions;
    log: LoadTestingApiLog;
    loadRecordingsCache: () => any;
    stringifyRecordings: (data: any) => string;
    persistRecordings: (data: string, newRequestIds: string[]) => void; // сохраняет записи в файл и загружает в S3
    createExpressProvider: (app: Express) => void;
    setPersistThresholdCallback: (callback: PersistThresholdCallback) => void;
    express: () => LoadTestingApiExpress;
};

export type LoadTestingApiLog = {
    debug: LogWriter;
    info: LogWriter;
    warn: LogWriter;
    error: LogWriter;
};

export type LoadTestingApiExpress = {
    getServer: () => PollyServer;
    setFixPathSearch: (bool: boolean) => void;
    setModifyHeadersHook: (hook: ModifyHeadersHook) => void;
    setModifyBodyHook: (hook: ModifyBodyHook) => void;
};

export type LogWriter = (message: string) => void;

export type ModifyHeadersHook = (headers: Headers, req: Request) => Headers;

export type ModifyBodyHook = (body: any, req: Request) => any;
