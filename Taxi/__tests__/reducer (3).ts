import {createStore, Store} from 'redux';

import {Order} from '../../../mapper/order-form/orders';
import toOrdersClient from '../../../mapper/order-form/orders/toOrdersClient';
import {setDraftFromOrder} from '../../draft/actions';
import {updateOrder} from '../actions';
import reducer, {initialState} from '../reducer';
import {State} from '../types';
import ordersResponse from './mocks/orders.json';

const PHONE_MOCK = '+79999999999';
const orders = toOrdersClient(PHONE_MOCK)(ordersResponse);
const mockedOrder = orders[0];

describe('/orders/reducer/setDraftFromOrder', () => {
    let store: Store<State>;
    let order: Order;
    beforeEach(() => {
        order = {...mockedOrder};
    });

    it('Должен сбросить выбранный order', () => {
        store = createStore(reducer, {
            ...initialState,
            selected: order,
        });
        store.dispatch(setDraftFromOrder(order));
        expect(store.getState().selected).toEqual(initialState.selected);
    });
});

describe('/orders/reducer/updateOrder', () => {
    it('Должен обновить первый заказ', () => {
        const order: Order = {...mockedOrder};
        const nextOrder: Order = {
            ...order,
            userid: 'b60002f6f1e79f4f56d48873096cf212',
        };
        const state = {
            ...initialState,
            orders: [order],
        };
        const store: Store<State> = createStore(reducer, state);

        store.dispatch(updateOrder({
            order,
            nextOrder,
        }));

        expect(store.getState().orders).not.toEqual(orders);
        expect(store.getState().orders[0].userid).not.toEqual(orders[0].userid);
    });

    it('Должен сбросить selected, если nextOrder не активный', () => {
        const order: Order = {...mockedOrder};
        const nextOrder: Order = {
            ...order,
            isActive: false,
        };
        const state = {
            orders: [order],
            selected: order,
        };
        const store: Store<State> = createStore(reducer, state);

        store.dispatch(updateOrder({
            order,
            nextOrder,
        }));

        expect(store.getState().selected).toEqual(initialState.selected);
    });

    it('Должен установить в selected nextOrder, если nextOrder активный', () => {
        const order: Order = {...mockedOrder};
        const nextOrder: Order = {
            ...order,
            isActive: true,
        };
        const state = {
            orders: [order],
            selected: order,
        };
        const store: Store<State> = createStore(reducer, state);

        store.dispatch(updateOrder({
            order,
            nextOrder,
        }));

        expect(store.getState().selected).toEqual(nextOrder);
    });
});
