import React from 'react';
import { cleanup } from 'react-testing-library';
import { TableWidget } from '..';
import { jestSnapshotRenderTest } from 'client/utils/jest-utils';

afterEach(cleanup);

jestSnapshotRenderTest({
    'with status loading': (
        <TableWidget
            status="loading"
            caption="Table widget caption"
            totals={[]}
            data={[]}
        />
    ),
    'with status error': (
        <TableWidget
            status="error"
            caption="Table widget caption"
            totals={[]}
            data={[]}
        />
    ),
    'with status success': (
        <TableWidget
            status="success"
            caption="Table widget caption"
            totals={[261]}
            data={[
                {
                    name:
                        'Очень длинное название, которое точно не влезет в одну строку, но которое попадет в таблицу 1',
                    value: 182,
                },
                {
                    name: 'Название, которое попадет в таблицу 2',
                    value: 182,
                },
                {
                    name: 'Название, которое не попадет в таблицу 3',
                    value: 182,
                },
                {
                    name: 'Название, которое попадет в таблицу 4',
                    value: 182,
                },
                {
                    name: 'Название, которое попадет в таблицу 5',
                    value: 182,
                },
            ]}
        />
    ),
});
