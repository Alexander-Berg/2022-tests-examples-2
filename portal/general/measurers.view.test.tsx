import { execView } from '@lib/views/execView';
import { Measurers__links } from '@block/measurers/measurers.view';
import { mockReq } from '@lib/views/mockReq';

describe('b-banner', function() {
    it('links', function() {
        expect(execView(Measurers__links, [
            'test.ru/?PAGEURL=[PAGEURL]&test=[test]&Y_DEVICE_TYPE=[Y_DEVICE_TYPE]&Y_AD_SESSION_ID=[Y_AD_SESSION_ID]',
            'test.ru/?PAGEURL=test=[test]',
            'test.ru'
        ], mockReq({
            isClient: false
        }, {
            Retpath: 'ya.ru%2Fatata%3Fsdfsdf%3Dqwe1',
            Requestid: '666'
        }))).toEqual([
            'test.ru/?PAGEURL=ya.ru%2Fatata%3Fsdfsdf%3Dqwe1&test=[test]&Y_DEVICE_TYPE=desktop&Y_AD_SESSION_ID=666',
            'test.ru/?PAGEURL=test=[test]',
            'test.ru'
        ]);
    });
});
