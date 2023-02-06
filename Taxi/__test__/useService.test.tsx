import {mount} from 'enzyme';
import React from 'react';
import {call, delay} from 'redux-saga/effects';

import useService from '_pkg/components/hooks/use-service';
import {sagaMiddleware} from '_pkg/infrastructure/store';
import {createService} from '_pkg/sagas/createService';
import {service} from '_pkg/sagas/services/FnComponentLoadService';

const processLoading = jest.fn((x: string) => ({}));
const processDisposing = jest.fn(() => ({}));

class TestServiceClass {
    public static toString = () => 'TestService';
}

const testService = createService(TestServiceClass, {
    onBeforeRun: processLoading as (x: string) => {},
    onBeforeDestroy: processDisposing
});

const TestComponent: React.FC<{}> = () => {
    useService(testService, ['1']);
    return null;
};

describe('useService', () => {
    beforeEach(() => {
        processLoading.mockClear();
        processDisposing.mockClear();
    });

    test('useService runs and destroys service', () => {
        return sagaMiddleware.run(function * () {
            yield call(service.run);

            const wrapper = mount(<TestComponent/>);
            yield delay(10);

            wrapper.unmount();
            yield delay(10);

            yield call(service.destroy);
        })
            .toPromise()
            .then(() => {
                expect(processLoading).toHaveBeenCalledTimes(1);
                expect(processLoading).toHaveBeenCalledWith('1');
                expect(processDisposing).toHaveBeenCalledTimes(1);
            });
    });
});
