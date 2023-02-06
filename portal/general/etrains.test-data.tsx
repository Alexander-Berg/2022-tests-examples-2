import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
/* eslint-disable @typescript-eslint/ban-ts-comment */
import { Script } from '@block/common/common.view';
// @ts-ignore
import { Etrains } from './etrains.view';

import preconfigured from './mocks/preconfigured.json';
import tunedEtrains from './mocks/tuned.json';
import ajaxResponse from './mocks/ajax-response.json';

export function simple() {
    const settingsJs = home.settingsJs([]);
    let req = mockReq({}, {
        settingsJs,
        ...preconfigured
    });

    return execView(Etrains, {}, req) + '<script>' + settingsJs.getRawScript(req) + '</script>';
}

export function tuned() {
    const settingsJs = home.settingsJs([]);
    let req = mockReq({}, {
        settingsJs,
        ...tunedEtrains
    });

    return execView(Script, {
        content: `
        $.get = function (url, callback) {
            callback(${JSON.stringify(ajaxResponse)});
            return $.Deferred();
        };
    `
    }) + execView(Etrains, {}, req) + '<script>' + settingsJs.getRawScript(req) + '</script>';
}
