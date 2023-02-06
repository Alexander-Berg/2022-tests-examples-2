import got from 'got';
import buildServerUrl from 'tests/e2e/utils/build-server-url';

import {config} from 'service/cfg';

import {routes} from './constants';

export async function getPort() {
    const {port} = await got.get<{port: number}>(buildServerUrl(routes.port(), config.server.balancerPort), {
        responseType: 'json',
        resolveBodyOnly: true
    });
    return port;
}

export async function getPorts() {
    const {ports} = await got.get<{ports: number[]}>(buildServerUrl(routes.ports(), config.server.balancerPort), {
        responseType: 'json',
        resolveBodyOnly: true
    });
    return ports;
}
