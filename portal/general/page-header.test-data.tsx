import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { PageHeader } from '@block/page-header/page-header.view';

export function simple() {
    return execView(PageHeader, {}, mockReq());
}
