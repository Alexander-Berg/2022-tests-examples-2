import metrics from '@blocks/metrics';

import * as actions from '../actions';

jest.mock('@blocks/metrics', () => ({
    send: jest.fn()
}));

describe('Dashboard.actions', () => {
    test('setPlusEnabled', () => {
        const value = 'value';

        expect(actions.setPlusEnabled(value)).toEqual({
            type: actions.SET_PLUS_ENABLED,
            enabled: value
        });
    });
    test('setPlusNextChargeTime', () => {
        const value = 'value';

        expect(actions.setPlusNextChargeTime(value)).toEqual({
            type: actions.SET_PLUS_NEXT_CHARGE_TIME,
            nextChargeTime: value
        });
    });

    describe('outOfBox', () => {
        it('should return 1d array', () => {
            const arr = [[1, 2], [3, 4], []];

            expect(actions.outOfBox(arr)).toEqual([1, 2, 3, 4]);
        });
        it('should return same object', () => {
            const obj = {some: 'some'};

            expect(actions.outOfBox(obj)).toBe(obj);
        });
    });
    describe('sendMetrics', () => {
        it('should call send of metrics', () => {
            const metricsData = {
                favMarketData: ['Избранное', 'Есть отложенные товары на маркете'],
                videoData: ['Избранное', 'Есть избранные видео'],
                collectionsData: ['Избранное', 'Есть коллекции'],
                musicData: ['Личный кабинет', 'Есть подписка на музыку'],
                afishaData: ['Личный кабинет', 'Есть билеты в афише'],
                marketData: ['Личный кабинет', 'Есть купленные товары']
            };

            for (const key in metricsData) {
                actions.sendMetrics(key);
                expect(metrics.send).toHaveBeenCalledTimes(1);
                expect(metrics.send).toHaveBeenCalledWith(metricsData[key]);
                metrics.send.mockClear();
            }
        });
        it('shouldnt call any send', () => {
            actions.sendMetrics('some');
            expect(metrics.send).toHaveBeenCalledTimes(0);
            metrics.send.mockClear();
        });
    });
    describe('getData', () => {
        const getState = () => ({person: {}, common: {}, settings: {lang: 'ru'}, publicId: {id: ''}});
        const dispatch = jest.fn();

        class Request {
            constructor() {
                this.done = this.handler.bind(this, 'onDone');
                this.fail = this.handler.bind(this, 'onFail');
            }
            handler(key, func) {
                this[key] = func;

                return this;
            }
        }

        afterEach(() => {
            dispatch.mockClear();
            metrics.send.mockClear();
        });
        it('should dispatch setData with musicData and call send of metrics', () => {
            const requests = [new Request()];

            actions.getData(undefined, function getRequests() {
                return {
                    videoDataCount: 2,
                    services: ['musicData'],
                    requests
                };
            })(dispatch, getState);
            requests[0].onDone({dateParts: true});
            expect(dispatch).toHaveBeenCalledTimes(2);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.SET_DB_DATA,
                data: {isLoading: true},
                service: 'musicData'
            });
            expect(dispatch.mock.calls[1][0]).toEqual({
                type: actions.SET_DB_DATA,
                data: {dateParts: true},
                service: 'musicData'
            });
            expect(metrics.send).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledWith(['Личный кабинет', 'Есть подписка на музыку']);
        });
        it('should dispatch setData with videoData and call send of metrics', () => {
            const requests = [new Request(), new Request()];
            const data = {
                page: 1,
                items: [1]
            };

            actions.getData(undefined, function getRequests() {
                return {
                    videoDataCount: 2,
                    services: ['videoData', 'videoData'],
                    requests
                };
            })(dispatch, getState);
            requests[0].onDone(data);
            data.page++;
            requests[1].onDone(data);
            expect(dispatch).toHaveBeenCalledTimes(2);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.SET_DB_DATA,
                data: {isLoading: true},
                service: 'videoData'
            });
            expect(dispatch.mock.calls[1][0]).toEqual({
                type: actions.SET_DB_DATA,
                data: {items: [1, 1]},
                service: 'videoData'
            });
            expect(metrics.send).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledWith(['Избранное', 'Есть избранные видео']);
        });
        it('should call fail which will dispatch setData', () => {
            const requests = [new Request()];

            actions.getData(undefined, function getRequests() {
                return {
                    videoDataCount: 2,
                    services: ['videoData'],
                    requests
                };
            })(dispatch, getState);
            requests[0].onDone();
            expect(dispatch).toHaveBeenCalledTimes(2);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.SET_DB_DATA,
                data: {isLoading: true},
                service: 'videoData'
            });
            expect(dispatch.mock.calls[1][0]).toEqual({
                type: actions.SET_DB_DATA,
                data: {errors: ['exception.unhandled']},
                service: 'videoData'
            });
        });
        it('should call fail with custom errors which will dispatch setData', () => {
            const requests = [new Request()];

            actions.getData(undefined, function getRequests() {
                return {
                    videoDataCount: 2,
                    services: ['videoData'],
                    requests
                };
            })(dispatch, getState);
            requests[0].onFail({errors: ['error']});
            expect(dispatch).toHaveBeenCalledTimes(2);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.SET_DB_DATA,
                data: {isLoading: true},
                service: 'videoData'
            });
            expect(dispatch.mock.calls[1][0]).toEqual({
                type: actions.SET_DB_DATA,
                data: {errors: ['error']},
                service: 'videoData'
            });
        });
    });
});
