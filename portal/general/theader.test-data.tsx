import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { Theader } from '@block/theader/theader.view';
import { Mlogo__resources } from '@block/mlogo/mlogo.view';

export function simple() {
    const req = mockReq();
    const resources = new home.Resources('touch', req, execView);
    req.resources = resources as typeof req['resources'];

    execView(Mlogo__resources, {}, req);
    const html =  execView(Theader, {}, req);

    return resources.getHTML('head') + html;
}
