import { execView } from '@lib/views/execView';
import { DistPopup__flags } from '@block/dist-popup/__flags/dist-popup__flags.view';

describe('dist-popup__flags', function() {
    describe('yabs', function() {
        it('no type', function() {
            expect(execView(DistPopup__flags, {
                from_yabs: true
            } as Req3DistPopup)).toEqual({
                isInnerAction: false,
                source: 'yabs',
                type: undefined
            });
        });
        it('type=download', function() {
            expect(execView(DistPopup__flags, {
                from_yabs: true,
                type: 'download'
            } as Req3DistPopup)).toEqual({
                isInnerAction: true,
                source: 'yabs',
                type: 'download'
            });
        });
    });

    describe('madm export', function() {
        it('product=browser', function() {
            expect(execView(DistPopup__flags, {
                product: 'browser'
            } as Req3DistPopup)).toEqual({
                isInnerAction: false,
                source: 'export',
                type: undefined
            });
        });
    });
});
