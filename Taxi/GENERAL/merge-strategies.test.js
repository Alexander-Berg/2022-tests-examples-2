import {mergeUpdatedEntities, mergeUpdatedEntity} from './merge-strategies';

describe('MergeStrategies', () => {
    describe('mergeUpdatedEntity', () => {
        test('добавляет или обновляет сущность', () => {
            expect(mergeUpdatedEntity('users', {_id: 'test'})({})).toEqual({
                users: {test: {_id: 'test'}},
            });
            expect(
                mergeUpdatedEntity('users', {_id: 'test', name: 'ivan'})({
                    users: {test: {_id: 'test', name: 'fedor'}},
                }),
            ).toEqual({users: {test: {_id: 'test', name: 'ivan'}}});
        });
    });

    describe('mergeUpdatedEntities', () => {
        test('добавляет или обновляет сущности массивом', () => {
            expect(mergeUpdatedEntities('users', [{_id: 'test'}, {_id: 'test2'}])({})).toEqual({
                users: {test: {_id: 'test'}, test2: {_id: 'test2'}},
            });
            expect(
                mergeUpdatedEntities('users', [
                    {_id: 'test', name: 'ivan'},
                    {_id: 'test2', name: 'maria'},
                ])({
                    users: {test: {_id: 'test', name: 'fedor'}},
                }),
            ).toEqual({
                users: {
                    test: {_id: 'test', name: 'ivan'},
                    test2: {_id: 'test2', name: 'maria'},
                },
            });
        });
    });
});
