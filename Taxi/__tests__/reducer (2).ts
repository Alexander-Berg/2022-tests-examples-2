import {OrderStatus} from '@yandex-taxi/js-integration-api';
import {createStore, Store} from 'redux';

import {Order} from '../../../mapper/order-form/orders';
import toOrdersClient from '../../../mapper/order-form/orders/toOrdersClient';
import {FocusFields} from '../../app/types';
import {setDraftFromOrder} from '../../draft/actions';
import {updateOrder} from '../../orders/actions';
import reducer, {initialState} from '../reducer';
import {State} from '../types';
import ordersResponse from './mocks/orders.json';

const PHONE_MOCK = '+79999999999';
const orders = toOrdersClient(PHONE_MOCK)(ordersResponse);
const mockedOrder = orders[0];

describe('/focus-element/reducer/setDraftFromOrder', () => {
    let order: Order;
    beforeEach(() => {
        order = {...mockedOrder};
    });

    it('Должен установить фокус на точку А, если в заказе есть телефон', () => {
        const store: Store<State> = createStore(reducer, initialState);

        store.dispatch(setDraftFromOrder(order));
        expect(store.getState()).toEqual({
            forcedId: FocusFields.Route0,
        });
    });
});

describe('/focus-element/reducer/updateOrderReducer', () => {
    let store: Store<State>;

    beforeEach(() => {
        store = createStore(reducer, initialState);
    });

    it('Не должен изменять стейт при не отмененном заказе', () => {
        const order: Order = {
            ...mockedOrder,
        };
        const nextOrder: Order = {
            ...mockedOrder,
            status: OrderStatus.WAITING,
        };

        store.dispatch(updateOrder({order, nextOrder}));

        expect(store.getState()).toStrictEqual(initialState);
    });
});
