/* eslint-disable @typescript-eslint/ban-ts-comment */

import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
// @ts-ignore
import { Informer__stocks__arrow } from './informers_type_stocks.view';

describe('informers_type_stocks', function() {
    const ARROW_HIDDEN = '';
    const ARROW_UP = '<span  class="informer__stocks-delta" aria-label="stocks.up">↑</span>';
    const ARROW_DOWN = '<span  class="informer__stocks-delta" aria-label="stocks.down">↓</span>';
    const req = mockReq({}, {
        l10n(key: string) {
            return key;
        }
    });

    describe('arrow', function() {
        it('не показывается при нулевом изменении', function() {
            // @ts-expect-error
            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: 0
            })).toEqual(ARROW_HIDDEN);

            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: '0'
            })).toEqual(ARROW_HIDDEN);

            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: '+0'
            })).toEqual(ARROW_HIDDEN);

            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: '-0'
            })).toEqual(ARROW_HIDDEN);

            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: '+0.00'
            })).toEqual(ARROW_HIDDEN);

            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: '+0.00%'
            })).toEqual(ARROW_HIDDEN);
        });

        it('показывает стрелку вверх', function() {
            // @ts-expect-error
            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: 0.0001
            }, req)).toEqual(ARROW_UP);

            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: '1'
            }, req)).toEqual(ARROW_UP);

            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: '+1'
            }, req)).toEqual(ARROW_UP);

            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: '+01'
            }, req)).toEqual(ARROW_UP);

            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: '+0.01'
            }, req)).toEqual(ARROW_UP);

            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: '+0.01%'
            }, req)).toEqual(ARROW_UP);
        });

        it('показывает стрелку вниз', function() {
            // @ts-expect-error
            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: -0.0001
            }, req)).toEqual(ARROW_DOWN);

            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: '-1'
            }, req)).toEqual(ARROW_DOWN);

            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: '-01'
            }, req)).toEqual(ARROW_DOWN);

            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: '-0.01'
            }, req)).toEqual(ARROW_DOWN);

            expect(execView(Informer__stocks__arrow, {
                value: '123',
                delta_raw: '-0.01%'
            }, req)).toEqual(ARROW_DOWN);
        });
    });
});
