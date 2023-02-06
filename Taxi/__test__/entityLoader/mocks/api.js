import uuid from 'uuid';
import {forEach} from 'lodash';

export const DATA = (new Array(100)).fill(0).map((zero, index) => ({id: `${index + 1}`, val: 0}));

export const API_TIMEOUT = 10;

export default class FakeAPI {
    static toString = () => 'FakeAPI'

    request = ({limit, skip, timeout, ...rest}) => {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    items: skip !== undefined && limit !== undefined ? DATA.slice(skip, skip + limit) : [...DATA],
                    meta: rest
                });
            }, timeout || API_TIMEOUT);
        });
    }

    create = (data, timeout) => {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    ...data,
                    id: uuid()
                });
            }, timeout || API_TIMEOUT);
        });
    }

    update = (data, timeout) => {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    ...data,
                    val: data.val + 1
                });
            }, timeout || API_TIMEOUT);
        });
    }

    remove = (data, timeout) => {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve();
            }, timeout || API_TIMEOUT);
        });
    }

    find = (id, timeout) => {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve();
            }, timeout || API_TIMEOUT);
        });
    }
}

export const apiInstance = new FakeAPI();

export const getMockedInstance = () => {
    const instance = new FakeAPI();
    forEach(instance, (method, name) => {
        instance[name] = jest.fn(method);
    });

    return instance;
};
