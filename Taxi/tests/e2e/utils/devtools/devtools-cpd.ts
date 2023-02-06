/* eslint-disable @typescript-eslint/no-explicit-any */
import CDP from 'chrome-remote-interface';

import {formatDevtoolsUrl, FormatDevtoolsUrlOptions} from './devtools-url';
import {handleLoadingFailed, handleRequestWillBeSent, makeHandleResponseReceived} from './handlers';
import {logMessage} from './log';

interface EnableDevtoolsNetworkOptions extends FormatDevtoolsUrlOptions {
    logResponseBody?: boolean;
}

/**
 * Не работает в чистом виде, потому что в селеноиде протокол реализован неточно.
 * При вызове этой функции происходит взрыв, селеноид должен ответить JSON-ом,
 * но отвечает простой строкой.
 */
export async function enableDevtoolsNetworkCPD(options: EnableDevtoolsNetworkOptions) {
    try {
        const target = formatDevtoolsUrl(options);
        const {Network} = await CDP({target});

        await Network.enable({});

        Network.on('requestWillBeSent', handleRequestWillBeSent as any);

        Network.on('loadingFailed', handleLoadingFailed as any);

        Network.on(
            'responseReceived',
            makeHandleResponseReceived((requestId: string) => {
                void Network.getResponseBody({requestId}).then(({body}) =>
                    logMessage({
                        title: 'response body',
                        message: body,
                        requestId
                    })
                );
            }) as any
        );
    } catch (err) {
        console.error(err);
    }
}
