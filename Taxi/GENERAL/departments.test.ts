import {DepartmentsHashTable} from '../api/departments/types';

import {getDepsWithChildren} from './departments';

const DEPARTMENTS_HASH: DepartmentsHashTable = {
    '1': {
        _id: '1',
        parent_id: '2',
        name: '',
    },
    '2': {
        _id: '2',
        parent_id: '3',
        name: '',
    },
    '3': {
        _id: '3',
        parent_id: null,
        name: '',
    },
    '4': {
        _id: '4',
        parent_id: null,
        name: '',
    },
    '5': {
        _id: '3',
        parent_id: '2',
        name: '',
    },
};

test('getDepsWithChildren', () => {
    const res = getDepsWithChildren(DEPARTMENTS_HASH);

    expect(res).toEqual({
        '1': {_id: '1', parent_id: '2', name: ''},
        '2': {_id: '2', parent_id: '3', name: '', children: ['1', '5']},
        '3': {_id: '3', parent_id: null, name: '', children: ['2']},
        '4': {_id: '4', parent_id: null, name: ''},
        '5': {_id: '3', parent_id: '2', name: ''},
    });
});
