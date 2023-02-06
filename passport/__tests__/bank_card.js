import {push} from 'react-router-redux';

import {EDIT_MODE_NAME, CARDS_LINK} from '@blocks/morda/cards';

import {BILLING_METRICS_PREFIX, BILLING_GOAL_PREFIX} from '@blocks/morda/billing_info';
import {setEditMode} from '@blocks/common/actions';
import {selectCard} from '@blocks/morda/cards/actions';

import metrics from '@blocks/metrics';

import * as extracted from '../bank_card.js';

jest.mock('react-router-redux', () => ({
    push: jest.fn()
}));
jest.mock('@blocks/common/actions', () => ({
    setEditMode: jest.fn()
}));
jest.mock('@blocks/morda/cards/actions', () => ({
    selectCard: jest.fn()
}));
jest.mock('@blocks/metrics', () => ({
    send: jest.fn(),
    goal: jest.fn()
}));

describe('Morda.BankCards.BankCard', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            props: {
                isTouch: false,
                dispatch: jest.fn(),
                card: {
                    id: 1
                }
            }
        };
    });

    describe('construct', () => {
        it('should find bank', () => {
            extracted.construct.call(obj, {
                card: {
                    number: '515876'
                }
            });
            expect(obj.bank).toBe('raiffeisen');
        });
        it('should fallback bank to light', () => {
            extracted.construct.call(obj, {
                card: {
                    number: '000000'
                }
            });
            expect(obj.bank).toBe('light');
        });
    });
    describe('selectBankCard', () => {
        afterEach(() => {
            metrics.send.mockClear();
            metrics.goal.mockClear();
        });

        test('if desktop', () => {
            extracted.selectBankCard.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(selectCard).toHaveBeenCalledTimes(1);
            expect(selectCard).toHaveBeenCalledWith(obj.props.card.id);
            expect(setEditMode).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledWith(EDIT_MODE_NAME);
            expect(metrics.goal).toHaveBeenCalledTimes(1);
            expect(metrics.goal).toHaveBeenCalledWith(`${BILLING_GOAL_PREFIX}edit`);
            expect(metrics.send).toHaveBeenCalledTimes(2);
            expect(metrics.send.mock.calls[0][0]).toEqual([BILLING_METRICS_PREFIX, 'Редактировать']);
            expect(metrics.send.mock.calls[1][0]).toEqual([BILLING_METRICS_PREFIX, 'Открыли попап']);
        });
        test('if mobile', () => {
            obj.props.isTouch = true;

            extracted.selectBankCard.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledWith(CARDS_LINK);
            expect(metrics.goal).toHaveBeenCalledTimes(1);
            expect(metrics.goal).toHaveBeenCalledWith(`${BILLING_GOAL_PREFIX}edit`);
            expect(metrics.send).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledWith([BILLING_METRICS_PREFIX, 'Редактировать']);
        });
        test('if no card', () => {
            delete obj.props.card;
            extracted.selectBankCard.call(obj);
            expect(selectCard).toHaveBeenCalledWith(undefined);
        });
    });
});
