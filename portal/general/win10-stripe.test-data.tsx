import { mockReq } from '@lib/views/mockReq';
import { execView } from '@lib/views/execView';
import { Win10Stripe } from '@block/win10-stripe/win10-stripe.view';

import mock from './mocks/index.json';

export function simple() {
    return (
        <>
            <style>{'body{font:13px Arial,sans-serif;}'}</style>
            {execView(Win10Stripe, {}, mockReq({}, mock))}
        </>
    );
}
