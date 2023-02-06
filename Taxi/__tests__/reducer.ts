import {createStore, Store} from 'redux';

import {Order} from '../../../mapper/order-form/orders';
import toOrdersClient from '../../../mapper/order-form/orders/toOrdersClient';
import {Requirement} from '../../../mapper/order-form/zone-info';
import {startEditOrder, stopEditOrder} from '../../orders/actions';
import {setDraftFromOrder} from '../actions';
import reducer from '../reducer';
import {reduceByWeight} from '../reducers/set-requirement';
import {initialState} from '../selectors';
import {State} from '../types';
import draft from './mocks/draft.json';
import ordersResponse from './mocks/orders.json';

const PHONE_MOCK = '+79999999999';
const orders = toOrdersClient(PHONE_MOCK)(ordersResponse);
const mockedOrder = orders[0];

describe('/draft/reducer/setDraftFromOrderReducer', () => {
    let store: Store<State>;
    let order: Order;

    beforeEach(() => {
        store = createStore(reducer, initialState);
        order = {...mockedOrder};
    });

    it('Должен установить черновик заказа', () => {
        store.dispatch(setDraftFromOrder(order));

        expect(store.getState()).toEqual(draft);
    });

    it('Должен устанавливать телефон для неактивного заказа', () => {
        order.isActive = false;
        store.dispatch(setDraftFromOrder(order));

        // Здесь мы не проверяем правильность установки телефона,
        // потому что это ответственность другого редьюсера
        expect(store.getState().phone).not.toEqual(initialState.phone);
    });

    it('Должен установить требования, если они есть в заказе', () => {
        order.request.requirements = {
            notEmpty: ['1'],
        };
        store.dispatch(setDraftFromOrder(order));

        expect(store.getState().requirements).not.toEqual(initialState.requirements);
    });

    it('Не должен устанавливать требования, если их нет в заказе', () => {
        order.request.requirements = null;
        store.dispatch(setDraftFromOrder(order));

        expect(store.getState().requirements).toEqual(initialState.requirements);
    });
});

describe('/draft/reducer/startEditOrder', () => {
    let store: Store<State>;
    let order: Order;

    beforeEach(() => {
        store = createStore(reducer, {
            ...initialState,
        });
        order = {...mockedOrder};
    });

    it('Должен установить черновик на выбор заказа', () => {
        store.dispatch(startEditOrder(order));

        expect(store.getState()).toEqual(draft);
    });
});

describe('/draft/reducer/stopEditOrder', () => {
    let store: Store<State>;

    beforeEach(() => {
        store = createStore(reducer, initialState);
    });

    it('Должен сбросить черновик', () => {
        store.dispatch(stopEditOrder());

        expect(store.getState()).toEqual(initialState);
    });
});

describe('/draft/reducer/setRequirement/reduceByWeight', () => {
    it('Должен оставить все требования на месте', () => {
        const values = [1, 2, 3];
        const requirement: Requirement = {
            name: 'A',
            type: 'number',
            maxWeight: 5,
            options: [
                {
                    value: 1,
                    weight: 2,
                    title: 'A',
                },
                {
                    value: 2,
                    weight: 2,
                    title: 'A',
                },
                {
                    value: 3,
                    weight: 1,
                    title: 'A',
                },
            ],
        };

        expect(values.reduce(reduceByWeight(requirement), [])).toEqual(values);
    });

    it('Должен удалить первое требование', () => {
        const values = [1, 2, 3];
        const requirement: Requirement = {
            name: 'A',
            type: 'number',
            maxWeight: 5,
            options: [
                {
                    value: 1,
                    weight: 3,
                    title: 'A',
                },
                {
                    value: 2,
                    weight: 2,
                    title: 'A',
                },
                {
                    value: 3,
                    weight: 1,
                    title: 'A',
                },
            ],
        };

        expect(values.reduce(reduceByWeight(requirement), [])).toEqual([2, 3]);
    });

    it('Должен удалить второе требование', () => {
        const values = [1, 2, 3];
        const requirement: Requirement = {
            name: 'A',
            type: 'number',
            maxWeight: 5,
            options: [
                {
                    value: 1,
                    weight: 1,
                    title: 'A',
                },
                {
                    value: 2,
                    weight: 4,
                    title: 'A',
                },
                {
                    value: 3,
                    weight: 2,
                    title: 'A',
                },
            ],
        };

        expect(values.reduce(reduceByWeight(requirement), [])).toEqual([1, 3]);
    });

    it('Должен оставить только последнее требование', () => {
        const values = [1, 2, 3];
        const requirement: Requirement = {
            name: 'A',
            type: 'number',
            maxWeight: 5,
            options: [
                {
                    value: 1,
                    weight: 1,
                    title: 'A',
                },
                {
                    value: 2,
                    weight: 4,
                    title: 'A',
                },
                {
                    value: 3,
                    weight: 5,
                    title: 'A',
                },
            ],
        };

        expect(values.reduce(reduceByWeight(requirement), [])).toEqual([3]);
    });
});
