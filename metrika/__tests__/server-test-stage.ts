import type Fetch from 'node-fetch';
import type { Response } from 'node-fetch';
import { HttpHeader } from '@shared/http/http-header';
import { HttpServerOptions } from '@server-libs/http-server/options';
import { HttpServer } from '@server-libs/http-server/server';
import { INTERNAL_ERROR, RuntimeError } from '@server-libs/node-tools/error';
import { HttpMethod } from '@server-libs/http-server/method';
import { ContentType } from '@server-libs/http-server/content-type';
import { HttpCode } from '@shared/http/code';

const { default: fetch } = jest.requireActual<{ default: typeof Fetch }>('node-fetch');

interface TestServerResponse<T> {
    headers: Record<HttpHeader, string | null>;
    code: HttpCode;
    data: T;
}

interface RequestOptions {
    headers?: Record<HttpHeader | string, string>;
    cookies?: Record<string, string>;
}

export class ServerTestStage {
    private server: HttpServer;

    private static serializeCookies(cookies: Record<string, string>): string {
        return Object.entries(cookies)
            .map(([name, value]) => `${name}=${value}`)
            .join('; ');
    }

    constructor(params: HttpServerOptions, private port: number) {
        this.server = new HttpServer(params);
    }

    async start(): Promise<void> {
        try {
            await this.server.start(this.port);
        } catch (error) {
            if ((<Error & { code: string }>error).code === 'EADDRINUSE') {
                throw new RuntimeError(INTERNAL_ERROR, `PORT ${this.port} in use`, error);
            }
            throw error;
        }
    }

    async stop(): Promise<void> {
        await this.server.stop();
    }

    isActive(): boolean {
        return this.server.isActive();
    }

    async requestData<D, B>(
        route: string,
        method?: HttpMethod,
        body?: B,
        options?: RequestOptions
    ): Promise<TestServerResponse<D>> {
        const response = await this.request(route, method, body, options);
        const json = <D>await response.json();

        return this.processResponse(response, json);
    }

    async requestText(
        route: string,
        method?: HttpMethod,
        options?: RequestOptions
    ): Promise<TestServerResponse<string>> {
        const response = await this.request(route, method, null, options);
        const text = await response.text();

        return this.processResponse(response, text);
    }

    private async request<T>(
        route: string,
        method: HttpMethod = HttpMethod.Get,
        body?: T,
        { headers = {}, cookies }: RequestOptions = {}
    ): Promise<Response> {
        const cookie = [
            headers.cookie ? `${headers.cookie}; ` : '',
            cookies ? ServerTestStage.serializeCookies(cookies) : '',
        ].join('');

        return fetch(`http://localhost:${this.port}/${route.startsWith('/') ? route.slice(1) : route}`, {
            method,
            body: body ? JSON.stringify(body) : undefined,
            headers: {
                ...(body && {
                    [HttpHeader.ContentType]: ContentType.ApplicationJson,
                }),
                ...headers,
                cookie,
            },
        });
    }

    private processResponse<T>(response: Response, data: T): TestServerResponse<T> {
        return {
            headers: Object.values(HttpHeader).reduce((acc, headerName) => {
                const value = response.headers.get(headerName.toLowerCase());
                if (value) {
                    acc[headerName] = value;
                }
                return acc;
            }, {} as Record<HttpHeader, string | null>),
            code: response.status,
            data,
        };
    }
}
