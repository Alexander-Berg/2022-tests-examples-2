import { execView } from '@lib/views/execView';
import { MockedInterface, mockReq } from '@lib/views/mockReq';
import { Informers } from '@block/informers/informers.view';

import mockSimple from './mocks/simple.json';

export function simple() {
    const req = mockReq({}, mockSimple);
    const resources = new home.Resources('white', req, execView);
    req.resources = resources as MockedInterface<home.Resources>;

    return execView(Informers, {}, req) +
        resources.getHTML('head');
}
