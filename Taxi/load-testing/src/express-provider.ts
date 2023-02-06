import NodeHttpAdapter from '@pollyjs/adapter-node-http';
import type {Express} from 'express';
import {get as getByPath} from 'lodash';

import {loadTesting} from '.';
import {ReactivePersister} from './reactive-persister';
import {ReactivePolly as Polly} from './reactive-polly';
import type {EnabledLoadTesting, LoadTestingApiExpress, ModifyBodyHook, ModifyHeadersHook} from './types';

Polly.register(NodeHttpAdapter);

let api: EnabledLoadTesting['api'];

export class ExpressProvider implements LoadTestingApiExpress {
    protected app: Express;
    protected polly: Polly;
    protected fixPathSearch?: boolean;
    protected modifyHeadersHook?: ModifyHeadersHook;
    protected modifyBodyHook?: ModifyBodyHook;

    public constructor(app: Express) {
        this.app = app;
        api = (loadTesting as EnabledLoadTesting).api;
        this.polly = this.initPolly();

        api.log.info('Created express provider');
    }

    public getServer() {
        return this.polly.server;
    }

    /**
     * Иногда перехватчик запросов теряет `search` часть запроса
     * (например, при запросах к tvm через пакет `@yandex-int/express-tvm`)
     * для этих случаев можно включить фикс-костыль
     */
    public setFixPathSearch(bool: boolean) {
        this.fixPathSearch = bool;
    }

    public setModifyHeadersHook(hook: ModifyBodyHook) {
        this.modifyHeadersHook = hook;
    }

    public setModifyBodyHook(hook: ModifyHeadersHook) {
        this.modifyBodyHook = hook;
    }

    protected initPolly() {
        const mode = 'replay';

        api.log.info(`Starting PollyJS :: ${mode}`);

        const polly = new Polly(api.options.recordingName, {
            adapters: ['node-http'],
            persister: ReactivePersister,
            logging: api.options.polly.logging
        });

        polly.configure({
            mode,
            recordIfMissing: true,
            recordFailedRequests: true,
            persisterOptions: {
                keepUnusedRequests: true, // не удалять неиспользованные записи
                disableSortingHarEntries: true
            },
            matchRequestsBy: {
                body: (body, req) => {
                    if (this.modifyBodyHook) {
                        body = this.modifyBodyHook(body, req);
                    }

                    api.log.debug(`${this.getRequestName(req)} :: BODY :: ${String(body)}`);

                    return body;
                },
                headers: (headers, req) => {
                    if (this.fixPathSearch) {
                        const originalUrl = req.url;
                        const url = new URL(originalUrl);
                        const actualPath = url.pathname + url.search;
                        const expectedPath = getByPath(req, ['requestArguments', 'req', 'path']);

                        if (actualPath !== expectedPath) {
                            const fixedUrl = url.origin + expectedPath;
                            req.url = fixedUrl;
                            api.log.warn(`Updated request url: "${fixedUrl}" (original: "${originalUrl}")`);
                        }
                    }

                    if (this.modifyHeadersHook) {
                        headers = this.modifyHeadersHook(headers, req);
                    }

                    api.log.debug(`${this.getRequestName(req)} :: HEADERS :: ${JSON.stringify(headers)}`);

                    return headers;
                },
                order: false
            }
        });

        return polly;
    }

    protected getRequestName({method, url}: {method: string; url: string}) {
        return [method, url].join(':');
    }
}
