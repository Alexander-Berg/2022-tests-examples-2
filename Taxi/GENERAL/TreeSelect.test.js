import {createParentMap, sortHierarchy} from './TreeSelect';

describe('createParentMap', () => {
    it('создаёт карту родителей из массива', () => {
        const departments = [
            {value: 'parent', parent_id: undefined, label: 'parent'},
            {value: 'child', parent_id: 'parent', label: 'child'},
            {value: 'grandchild', parent_id: 'child', label: 'grand'},
        ];
        const map = {
            parent: departments[0],
            child: departments[1],
            grandchild: departments[2],
        };
        expect(createParentMap(departments, map)).toEqual({
            parent: ['child'],
            child: ['grandchild'],
        });
    });
});

describe('sortHierarchy', () => {
    it('сортирует массив по родителям и расставляет отступы', () => {
        expect(
            sortHierarchy([
                {value: 'child', parent_id: 'parent', label: 'child'},
                {value: 'parent', parent_id: undefined, label: 'parent'},
                {value: 'stranger', parent_id: undefined, label: 'stranger'},
                {value: 'grandchild', parent_id: 'child', label: 'grand'},
            ]),
        ).toEqual([
            {value: 'parent', parent_id: undefined, label: 'parent', depth: 0},
            {value: 'child', parent_id: 'parent', label: 'child', depth: 1},
            {value: 'grandchild', parent_id: 'child', label: 'grand', depth: 2},
            {
                value: 'stranger',
                parent_id: undefined,
                label: 'stranger',
                depth: 0,
            },
        ]);
    });
});
