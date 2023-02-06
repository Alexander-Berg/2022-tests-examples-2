/* eslint-disable max-len */
import {
    addToTree,
    getAllChildrenFromResults,
    mapDepartmentsToDescendantsChain,
    mapDepartmentToParentChain,
    mapIDChainsToDepartmentTree,
    mapIDsToDescendantChains,
    mapIDsToRootAndByParent,
    reduceChain,
    removeDepartmentWithChildren,
    removeFromResults,
} from './department';

describe('api/department', () => {
    const department = {
        _id: 'child',
        parents: [{_id: 'parent'}, {_id: 'grandparent'}],
    };
    describe('mapDepartmentsToDescendantsChain', () => {
        test('Должен слеплять департаменты в один массив', () => {
            expect(mapDepartmentToParentChain(department)).toMatchObject([
                {_id: 'child'},
                {_id: 'parent'},
                {_id: 'grandparent'},
            ]);
        });
    });
    describe('mapDepartmentsToParentIDChain', () => {
        test('Из департамента с его parents должен получиться массив из ID в порядке иерарахии', () => {
            expect(mapDepartmentsToDescendantsChain([department])).toMatchObject([
                ['grandparent', 'parent', 'child'],
            ]);
        });
    });
    describe('addToTree', () => {
        test('Должна добавлять отношение parent-child в дерево', () => {
            expect(addToTree({}, 'a', 'b')).toMatchObject({
                a: ['b'],
            });
            expect(addToTree({a: ['b']}, 'a', 'c')).toMatchObject({
                a: ['b', 'c'],
            });
        });
        test('Должна не допускать дубликатов', () => {
            expect(addToTree({a: ['b']}, 'a', 'b')).toMatchObject({
                a: ['b'],
            });
        });
    });
    describe('reduceChain', () => {
        test('Должна добавлять цепочки родительства', () => {
            expect(reduceChain({}, ['a', 'b', 'c'])).toMatchObject({
                a: ['b'],
                b: ['c'],
            });
            expect(reduceChain({a: ['b']}, ['a', 'c', 'd'])).toMatchObject({
                a: ['b', 'c'],
                c: ['d'],
            });
        });
    });
    describe('mapChainsToDepartmentTree', () => {
        test('Должна преобразовывать цепочки наследования в карту', () => {
            expect(
                mapIDChainsToDepartmentTree([
                    ['a', 'b', 'c'],
                    ['a', 'b', 'c', 'd', 'e'],
                ]),
            ).toMatchObject({
                a: ['b'],
                b: ['c'],
                c: ['d'],
                d: ['e'],
            });
        });
    });
    describe('removeDepartmentWithChildren', () => {
        test('Должен удалять хотя бы сам департамент', () => {
            const departments = {
                a: {_id: 'a'},
            };
            expect(removeDepartmentWithChildren(departments, 'a').a).toBeUndefined();
        });
        test('Должен удалять детей первого уровня', () => {
            const departments = {
                parent: {_id: 'parent'},
                child: {_id: 'child', parent_id: 'parent'},
            };
            expect(removeDepartmentWithChildren(departments, 'parent').child).toBeUndefined();
        });
        test('Должен удалять детей второго уровня', () => {
            const departments = {
                parent: {_id: 'parent'},
                child: {_id: 'child', parent_id: 'parent'},
                grandchild: {_id: 'grandchild', parent_id: 'child'},
            };
            expect(removeDepartmentWithChildren(departments, 'parent').grandchild).toBeUndefined();
        });
    });
    describe('removeFromResults', () => {
        describe('getAllChildrenFromResults', () => {
            test('Должен собирать детей первого уровня', () => {
                const departments = {
                    parent: ['child1', 'child2'],
                };
                expect(getAllChildrenFromResults(departments, 'parent')).toEqual([
                    'child1',
                    'child2',
                ]);
            });
            test('Должен собирать детей второго уровня', () => {
                const departments = {
                    parent: ['child1', 'child2'],
                    child1: ['grandchild1'],
                    child2: ['grandchild2'],
                };
                expect(getAllChildrenFromResults(departments, 'parent')).toEqual([
                    'child1',
                    'child2',
                    'grandchild1',
                    'grandchild2',
                ]);
            });
        });
        test('Должен начисто удалять всё с детьми', () => {
            const departments = {
                available: ['parent', 'child1', 'child2', 'grandchild1', 'grandchild2'],
                root: ['parent'],
                byParent: {
                    parent: ['child1', 'child2'],
                    child1: ['grandchild1'],
                    child2: ['grandchild2'],
                },
            };
            expect(removeFromResults(departments, 'parent')).toEqual({
                available: [],
                root: [],
                byParent: {},
            });
        });

        test('Не должен падать при отсутствии byParent (хотя и удалять тоже при этом не может)', () => {
            const departments = {
                available: ['parent', 'child1', 'child2', 'grandchild1', 'grandchild2'],
                root: ['parent'],
            };
            expect(removeFromResults(departments, 'parent')).toEqual({
                available: ['child1', 'child2', 'grandchild1', 'grandchild2'],
                root: [],
                byParent: {},
            });
        });
    });
    describe('mapIDsToDescendantChains', () => {
        test('Превращает список идентификаторов в список цепочек', () => {
            const departments = {
                child: {_id: 'child', parent_id: 'parent'},
                parent: {_id: 'parent', parent_id: undefined},
                grandchild: {_id: 'grandchild', parent_id: 'child'},
            };
            expect(mapIDsToDescendantChains(departments, ['child'])).toEqual([['parent', 'child']]);
            expect(mapIDsToDescendantChains(departments, ['grandchild'])).toEqual([
                ['parent', 'child', 'grandchild'],
            ]);
            expect(mapIDsToDescendantChains(departments, ['parent'])).toEqual([['parent']]);
        });
    });
    describe('mapIDsToRootAndByParent', () => {
        test('Превращает список идентификаторов в списки по родителям', () => {
            const departments = {
                child: {_id: 'child', parent_id: 'parent'},
                parent: {_id: 'parent', parent_id: undefined},
                grandchild: {_id: 'grandchild', parent_id: 'child'},
            };
            expect(mapIDsToRootAndByParent(departments, ['child'])).toEqual({
                root: ['parent'],
                byParent: {parent: ['child']},
            });
            expect(mapIDsToRootAndByParent(departments, ['child', 'grandchild'])).toEqual({
                root: ['parent'],
                byParent: {parent: ['child'], child: ['grandchild']},
            });
        });
    });
});
