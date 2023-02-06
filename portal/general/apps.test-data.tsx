import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { Apps } from '@block/apps/apps.view';
import * as mock from './mocks/index.json';

export function simple() {
    return execView(Apps, {}, mockReq({}, mock));
}
