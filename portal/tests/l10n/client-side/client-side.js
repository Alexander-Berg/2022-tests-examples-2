import {home} from '../../../lib/home.js';

export * from './a.js';
export * from './b.js';
export * from './client.js';
export * from './direct-import';

export function execView(template, data, req) {
    req = req || {};

    req.l10n =  home.l10n;

    return template(data, req);
}

export function loadAsync() {
    return import(/* webpackChunkName: "header-async" */`./async`);
}
