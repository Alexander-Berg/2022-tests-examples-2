import {render} from '@testing-library/react';
import {noop} from 'lodash';
import React, {FC} from 'react';

import {DEFAULT_PAGINATION} from 'utils/reducers/flow';

import {
    ant2BackPagination,
    DEFAULT_VENDOR_PAGINATION,
    clearPaginator,
    renderPaginationWithDataCY,
} from '../pagination';

describe('ant2BackPagination tests', () => {
    test('it must return default pagination on empty call', () => {
        expect(ant2BackPagination()).toStrictEqual(DEFAULT_VENDOR_PAGINATION);
    });

    test('it must convert pagination correctly', () => {
        expect(ant2BackPagination({
            current: 5,
            pageSize: 50,
        })).toStrictEqual({
            limit: 50,
            offset: 200,
        });
    });

    test('it must return default pagination when current below zero', () => {
        expect(ant2BackPagination({
            current: -5,
            pageSize: 50,
        })).toStrictEqual(DEFAULT_VENDOR_PAGINATION);
    });

    test('it must return default pagination when pageSize below zero', () => {
        expect(ant2BackPagination({
            current: 5,
            pageSize: -50,
        })).toStrictEqual(DEFAULT_VENDOR_PAGINATION);
    });

    test('it must return default pagination when pageSize equal zero', () => {
        expect(ant2BackPagination({
            current: 5,
            pageSize: 0,
        })).toStrictEqual(DEFAULT_VENDOR_PAGINATION);
    });
});

describe('clearPaginator tests', () => {
    test('it must call passed function', () => {
        const mockCallback = jest.fn(noop);

        clearPaginator(mockCallback);
        expect(mockCallback.mock.calls.length).toBe(1);
    });

    test('it must pass default pagination to function', () => {
        const array: AntPaginationType[] = [];
        const action = (obj: AntPaginationType) => {
            array.push(obj);
        };

        clearPaginator(action);
        expect(array).toStrictEqual([DEFAULT_PAGINATION]);
    });
});

describe('renderPaginationWithDataCY tests', () => {
    const TestComponent: FC = () => <div className="test"/>;

    test('it must correctly wrap component', () => {
        // @ts-ignore тут какой-то долбанутый тип у антд
        const {container} = render(renderPaginationWithDataCY(0, 'next', <TestComponent/>));

        expect(container.querySelectorAll('[data-cy="pagination"]').length).toBe(1);
        expect(container.querySelectorAll('[data-cy="pagination"] .test').length).toBe(1);
    });
});
