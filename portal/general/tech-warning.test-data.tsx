import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { TechWarning } from '@block/tech-warning/tech-warning.view';
import * as mock from './mocks/index.json';

export function simple() {
    return execView(TechWarning, {}, mockReq({}, mock));
}

export function dark() {
    return {
        html: execView(TechWarning, {}, mockReq({}, mock)),
        skin: 'night'
    };
}
