import type Protocol from 'devtools-protocol';

import {logMessage} from './log';

export function handleRequestWillBeSent({type, request, requestId}: Protocol.Network.RequestWillBeSentEvent) {
    logMessage({
        type,
        title: 'Network.requestWillBeSent',
        requestId,
        message: `${request.method} ${request.url}`,
        meta: {headers: request.headers}
    });
}

export function handleRequestWillBeSentExtraInfo({
    headers,
    requestId
}: Protocol.Network.RequestWillBeSentExtraInfoEvent) {
    logMessage({
        title: 'Network.requestWillBeSentExtraInfo',
        requestId,
        message: '',
        meta: {headers}
    });
}

export function handleResponseReceivedExtraInfo({headers, requestId}: Protocol.Network.ResponseReceivedExtraInfoEvent) {
    logMessage({
        title: 'Network.responseReceivedExtraInfo',
        requestId,
        message: '',
        meta: {headers}
    });
}

export function handleLoadingFailed({type, errorText, requestId}: Protocol.Network.LoadingFailedEvent) {
    logMessage({
        type,
        title: 'Network.loadingFailed',
        requestId,
        message: errorText
    });
}

export function makeHandleResponseReceived(logResponseBody?: (requestId: string) => void) {
    return function handleResponseReceived({type, response, requestId}: Protocol.Network.ResponseReceivedEvent) {
        logMessage({
            type,
            title: 'Network.responseReceived',
            requestId,
            message: `${response.url} -> ${response.status}`,
            meta: {headers: response.headers}
        });

        logResponseBody?.(requestId);
    };
}
