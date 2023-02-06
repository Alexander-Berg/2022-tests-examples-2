import {getLimits} from '../matchers';
import {DEFAULT_DISCOUNT_MODEL} from './consts';

describe('getLimits', () => {
    it('undefined если все поля пусты', () => {
        expect(getLimits({
            ...DEFAULT_DISCOUNT_MODEL,
            limits: {
                daily_limit: '' as any as number,
                daily_threshold: '' as any as number,
                weekly_limit: '' as any as number,
                weekly_threshold: '' as any as number,
                check_current_week: false,
            },
        })).toBeUndefined();
    });

    it('Корректная конвертация', () => {
        expect(getLimits({
            ...DEFAULT_DISCOUNT_MODEL,
            limits: {
                daily_limit: '2' as any as number,
                daily_threshold: '3' as any as number,
                weekly_limit: '4' as any as number,
                weekly_threshold: '5' as any as number,
                check_current_week: true,
            },
        })).toEqual({
            daily_limit: {
                threshold: 3,
                value: '2',
            },
            weekly_limit: {
                threshold: 5,
                value: '4',
                check_current_week: true,
            }
        });

        expect(getLimits({
            ...DEFAULT_DISCOUNT_MODEL,
            limits: {
                daily_limit: '8' as any as number,
                daily_threshold: '9' as any as number,
                weekly_limit: '10' as any as number,
                weekly_threshold: '15' as any as number,
                check_current_week: false,
            },
        })).toEqual({
            daily_limit: {
                threshold: 9,
                value: '8',
            },
            weekly_limit: {
                threshold: 15,
                value: '10',
                check_current_week: false,
            }
        });
    });
});
