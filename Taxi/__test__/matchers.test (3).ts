import {isMoment} from 'moment';

import {Draft, DraftStatusEnum} from '_libs/drafts/types';

import {RuleEnum} from '../../enums';
import {DiscountRule} from '../../types';
import {postDraftFind} from '../matchers';

describe('postDraftFind', () => {
    test('должна конвертировать драфт discountPayback правил в модель правил', () => {
        const rule: DiscountRule = {
            kind: RuleEnum.Discount,
            id: '123',
            begin_at: '2019-01-01',
            end_at: '2019-01-02',
            zone: '125125sdba'
        };

        const draft: Draft<{
            rules: Array<DiscountRule>;
        }> = {
            status: DraftStatusEnum.NeedApproval,
            description: 'description',
            data: {
                rules: [rule]
            },
            id: 321
        };
        const {begin_at, end_at, ...result} = postDraftFind(draft, true) ?? {};

        expect(result).toEqual({
            $view: {commonFields: {description: 'description'}, draftInfo: undefined},
            end_time: '00:00',
            id: '321',
            kind: 'discount_payback',
            start_time: '00:00',
            zones: ['125125sdba'],
            log: []
        });
        expect(isMoment(begin_at)).toBeTruthy();
        expect(isMoment(end_at)).toBeTruthy();
    });
});
