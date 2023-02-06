import { execView } from '@lib/views/execView';
import { HomeLogo } from '@block/home-logo/home-logo.view';
import * as reqs from './mocks/index';

export function std() {
    return execView(HomeLogo, {}, reqs.std);
}

export function defaultLangTr() {
    return execView(HomeLogo, {}, reqs.defaultLangTr);
}

export function custom() {
    return execView(HomeLogo, {}, reqs.custom);
}

export function customOffsets() {
    return execView(HomeLogo, {}, reqs.customOffsets);
}
