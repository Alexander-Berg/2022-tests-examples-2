import React from 'react';
import {mount} from 'enzyme';

import {push} from 'react-router-redux';
import {getCardsInfo, createBinding, EDIT_MODE_NAME, CARDS_LINK} from '@blocks/morda/cards';
import {setEditMode} from '@blocks/common/actions';

import BankCards from '../bank_cards';
import * as extracted from '../bank_cards_extracted';

jest.mock('react-router-redux', () => ({
    push: jest.fn()
}));
jest.mock('@blocks/morda/cards', () => ({
    createBinding: jest.fn(),
    getCardsInfo: jest.fn()
}));
jest.mock('@blocks/common/actions', () => ({
    setEditMode: jest.fn()
}));

describe('Morda.BankCards', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            props: {
                dispatch: jest.fn(),
                billing: {
                    cards: []
                },
                retpath: 'retpath',
                settings: {
                    isTouch: false
                },
                edit: 'edit',
                staticPath: 'st'
            }
        };
    });
    describe('getCardsInfoIfNeeded', () => {
        it('should dispatch getCardsInfo', () => {
            delete obj.props.billing.cards;
            mount(<BankCards {...obj.props} />);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(getCardsInfo).toHaveBeenCalledTimes(1);
        });
        it('shouldnt dispatch', () => {
            mount(<BankCards {...obj.props} />);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(0);
        });
    });
    describe('bindCard', () => {
        it('should dispatch createBinding and setEditMode, and call preventDefault of event', () => {
            const event = {
                preventDefault: jest.fn()
            };

            extracted.bindCard.call(obj, event);

            expect(event.preventDefault).toHaveBeenCalledTimes(1);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(setEditMode).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledWith(EDIT_MODE_NAME);
            expect(createBinding).toHaveBeenCalledTimes(1);
        });
        it('should dispatch push and call preventDefault of event', () => {
            const event = {
                preventDefault: jest.fn()
            };

            obj.props.settings.isTouch = true;
            extracted.bindCard.call(obj, event);

            expect(event.preventDefault).toHaveBeenCalledTimes(1);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledWith(CARDS_LINK);
        });
    });
});
