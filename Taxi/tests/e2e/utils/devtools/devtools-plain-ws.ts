/* eslint-disable no-case-declarations */
import WebSocket from 'ws';

import {formatDevtoolsUrl, FormatDevtoolsUrlOptions} from './devtools-url';
import {
    handleLoadingFailed,
    handleRequestWillBeSent,
    handleRequestWillBeSentExtraInfo,
    handleResponseReceivedExtraInfo,
    makeHandleResponseReceived
} from './handlers';
import {logMessage} from './log';

interface EnableDevtoolsNetworkOptions extends FormatDevtoolsUrlOptions {
    logResponseBody?: boolean;
}

export async function enableDevtoolsNetworkPlainWS(options: EnableDevtoolsNetworkOptions) {
    try {
        const devtools = new DevtoolsClient(options);
        await devtools.sendCommand('Network.enable');
        devtools.addCDPEventListener('Network.requestWillBeSent', handleRequestWillBeSent);
        devtools.addCDPEventListener('Network.requestWillBeSentExtraInfo', handleRequestWillBeSentExtraInfo);
        devtools.addCDPEventListener(
            'Network.responseReceived',
            makeHandleResponseReceived(options.logResponseBody ? makeLogResponseBody(devtools) : undefined)
        );
        devtools.addCDPEventListener('Network.responseReceivedExtraInfo', handleResponseReceivedExtraInfo);
        devtools.addCDPEventListener('Network.loadingFailed', handleLoadingFailed);
    } catch (err) {
        console.error(err);
    }
}

function makeLogResponseBody(devtoolsClient: DevtoolsClient) {
    return function logResponseBody(requestId: string) {
        void devtoolsClient.sendCommand('Network.getResponseBody', {requestId}).then((res) => {
            logMessage({
                title: 'Network.getResponseBody',
                requestId,
                message: JSON.stringify(res.result?.params)
            });
        });
    };
}

interface DevtoolsResponseResult {
    method: string;
    params: unknown;
}

interface DevtoolsResponse {
    id: number;
    result?: DevtoolsResponseResult;
    error?: {
        code: number;
        message: string;
        data?: unknown;
    };
}

class DevtoolsClient {
    private _ws: WebSocket;

    private _isOpen = false;

    private _currentId = 0;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    private _messageHandlers = new Map<string, (params: any) => void>();

    constructor(options: EnableDevtoolsNetworkOptions) {
        this._ws = new WebSocket(formatDevtoolsUrl(options), {perMessageDeflate: false});
        this._ws.addEventListener('message', this._handleMessageEvent);
    }

    private _handleMessageEvent = ({data}: WebSocket.MessageEvent) => {
        try {
            const {method, params}: DevtoolsResponseResult = JSON.parse(data.toString());

            this._messageHandlers.get(method)?.(params);
        } catch (err) {
            console.error('Error while handling message', err);
        }
    };

    private async _waitForOpen() {
        if (this._isOpen) {
            return;
        }

        return new Promise<void>((resolve) => {
            this._ws.once('open', () => {
                this._isOpen = true;
                resolve();
            });
        });
    }

    async sendCommand(method: string, params: Record<string, unknown> = {}) {
        await this._waitForOpen();

        const id = this._currentId++;

        return new Promise<DevtoolsResponse>((resolve, reject) => {
            this._ws.send(JSON.stringify({id, method, params}), (err) => {
                if (err) {
                    return reject(err);
                }
            });

            const messageEventHandler = ({data}: WebSocket.MessageEvent) => {
                try {
                    const response: DevtoolsResponse = JSON.parse(data.toString());
                    if (response.id === id) {
                        this._ws.removeEventListener('message', messageEventHandler);
                        resolve(response);
                    }
                } catch (err) {
                    reject(err);
                }
            };

            this._ws.addEventListener('message', messageEventHandler);
        });
    }

    addCDPEventListener<P>(event: string, handler: (params: P) => void) {
        this._messageHandlers.set(event, handler);
    }

    dispose() {
        this._ws.removeAllListeners();
    }
}
