// tslint:disable:max-file-line-count

import {cloneDeep} from 'lodash';

import {DEFAULT_PADDING_PX} from '../consts';
import {FlatNode, Path, SelectTreeNode, TreeNode} from '../types';
import {
    checkSelected,
    filterFlatTree,
    flattenTree,
    getChildrenPaths,
    getExpandedNodes,
    getSelectItems,
    hasSelectedChildren,
    makeTreeDataFullPaths,
} from '../utils';

const baseTreeNode: SelectTreeNode = {
    title: '',
    value: 'parent',
    children: [
        {title: '', value: 'child1'},
        {
            title: '',
            value: 'child2',
            children: [
                {title: '', value: 'child2.1'},
                {title: '', value: 'child2.2'},
                {
                    title: '',
                    value: 'child2.3',
                    children: [
                        {title: '', value: 'child2.3.1'},
                        {title: '', value: 'child2.3.2'},
                    ],
                },
            ],
        },
        {title: '', value: 'child3'},
    ],
};

const viewTreeNode: TreeNode = {
    title: '',
    value: 'parent',
    path: ['parent'],
    children: [
        {
            title: '',
            value: 'child1',
            path: ['parent', 'child1'],
            children: [],
        },
        {
            title: '',
            value: 'child2',
            path: ['parent', 'child2'],
            children: [
                {
                    title: '',
                    value: 'child2.1',
                    path: ['parent', 'child2', 'child2.1'],
                    children: [],
                },
                {
                    title: '',
                    value: 'child2.2',
                    path: ['parent', 'child2', 'child2.2'],
                    children: [],
                },
                {
                    title: '',
                    value: 'child2.3',
                    path: ['parent', 'child2', 'child2.3'],
                    children: [
                        {
                            title: '',
                            value: 'child2.3.1',
                            path: ['parent', 'child2', 'child2.3', 'child2.3.1'],
                            children: [],
                        },
                        {
                            title: '',
                            value: 'child2.3.2',
                            path: ['parent', 'child2', 'child2.3', 'child2.3.2'],
                            children: [],
                        },
                    ],
                },
            ],
        },
        {
            title: '',
            value: 'child3',
            path: ['parent', 'child3'],
            children: [],
        },
    ],
};

const baseTreeData: SelectTreeNode[] = [
    {
        title: '',
        value: 'root 1',
        children: [
            {title: '', value: 'root 1.1'},
            {
                title: '',
                value: 'root 1.2',
                children: [
                    {title: '', value: 'root 1.2.1'},
                    {title: '', value: 'root 1.2.2'},
                ],
            },
            {title: '', value: 'root 1.3'},
        ],
    },
    {title: '', value: 'root 2'},
];

const viewTree: TreeNode[] = [
    {
        title: '',
        value: 'parent1',
        path: ['parent1'],
        children: [
            {
                title: '',
                value: 'child1',
                path: ['parent1', 'child1'],
            },
            {
                title: '',
                value: 'child2',
                path: ['parent1', 'child2'],
                children: [
                    {
                        title: '',
                        value: 'child2.1',
                        path: ['parent1', 'child2', 'child2.1'],
                    },
                ],
            },
            {
                title: '',
                value: 'child3',
                path: ['parent1', 'child3'],
            },
        ],
    },
    {
        title: '',
        value: 'parent2',
        path: ['parent2'],
    },
];

describe('makeTreeDataFullPaths', () => {
    it('Добавляет в treeData пути для всех нод', () => {
        const treeData: Array<SelectTreeNode> = [cloneDeep(baseTreeNode)];
        const fullPathsTreeData = makeTreeDataFullPaths(treeData);

        expect(fullPathsTreeData).toEqual([viewTreeNode]);
    });
});

describe('getChildrenPaths', () => {
    it('Получение путей всех детей ноды', () => {
        const node = cloneDeep(viewTreeNode);

        const result: Path[] = [
            ['parent', 'child1'],
            ['parent', 'child2'],
            ['parent', 'child2', 'child2.1'],
            ['parent', 'child2', 'child2.2'],
            ['parent', 'child2', 'child2.3'],
            ['parent', 'child2', 'child2.3', 'child2.3.1'],
            ['parent', 'child2', 'child2.3', 'child2.3.2'],
            ['parent', 'child3'],
        ];

        expect(getChildrenPaths(node.children)).toEqual(result);
    });
});

describe('getSelectItems', () => {
    const tree = makeTreeDataFullPaths(cloneDeep(baseTreeData));
    describe('checkable режим', () => {
        it('Выбор ноды дерева, при пустом массиве выбранных элементов', () => {
            const selectedItems: Path[] = [];
            const nodesPath = [tree[0], tree[0].children![1], tree[0].children![1].children![0]];

            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: true,
                }),
            ).toEqual([['root 1', 'root 1.2', 'root 1.2.1']]);

            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: true,
                    fullPath: true,
                }),
            ).toEqual([['root 1', 'root 1.2', 'root 1.2.1']]);
        });

        it('Выбор ноды дерева, когда соседние ноды уже выбраны', () => {
            const selectedItems: Path[] = [['root 1', 'root 1.2', 'root 1.2.2']];
            const nodesPath = [tree[0], tree[0].children![1], tree[0].children![1].children![0]];

            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: true,
                }),
            ).toEqual([['root 1', 'root 1.2']]);
            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: true,
                    fullPath: true,
                }),
            ).toEqual([['root 1', 'root 1.2']]);
        });

        it('Выбор ноды дерева, когда соседние ноды уже выбраны на нескольких уровнях', () => {
            const selectedItems: Path[] = [
                ['root 1', 'root 1.1'],
                ['root 1', 'root 1.2', 'root 1.2.2'],
                ['root 1', 'root 1.3'],
            ];
            const nodesPath = [tree[0], tree[0].children![1], tree[0].children![1].children![0]];

            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: true,
                }),
            ).toEqual([['root 1']]);

            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: true,
                    fullPath: true,
                }),
            ).toEqual([['root 1']]);
        });

        it('Выбор ноды дерева, когда дети не выбраны', () => {
            const selectedItems: Path[] = [];
            const nodesPath = [tree[0], tree[0].children![1]];

            expect(getSelectItems({selectedItems, nodesPath, checkable: true})).toEqual([['root 1', 'root 1.2']]);

            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: true,
                    fullPath: true,
                }),
            ).toEqual([['root 1', 'root 1.2']]);
        });

        it('Выбор ноды дерева, когда дети выбраны', () => {
            const selectedItems: Path[] = [['root 1', 'root 1.2', 'root 1.2.2']];
            const nodesPath = [tree[0], tree[0].children![1]];

            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: true,
                }),
            ).toEqual([['root 1', 'root 1.2']]);
            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: true,
                    fullPath: true,
                }),
            ).toEqual([['root 1', 'root 1.2']]);
        });

        it('Снятие выбора с ноды дерева', () => {
            const selectedItems: Path[] = [['root 2'], ['root 1', 'root 1.2', 'root 1.2.1']];
            const nodesPath = [tree[0], tree[0].children![1], tree[0].children![1].children![0]];

            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: true,
                }),
            ).toEqual([['root 2']]);
            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: true,
                    fullPath: true,
                }),
            ).toEqual([['root 2']]);
        });

        it('Снятие выбора с ноды дерева, у которой есть дети', () => {
            const selectedItems: Path[] = [['root 2'], ['root 1', 'root 1.2']];
            const nodesPath = [tree[0], tree[0].children![1]];

            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: true,
                }),
            ).toEqual([['root 2']]);
            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: true,
                    fullPath: true,
                }),
            ).toEqual([['root 2']]);
        });

        it('Снятие выбора с ноды, у которой выбран родитель', () => {
            const selectedItems: Path[] = [['root 1']];
            const nodesPath = [tree[0], tree[0].children![1], tree[0].children![1].children![0]];

            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: true,
                }),
            ).toEqual([
                ['root 1', 'root 1.2', 'root 1.2.2'],
                ['root 1', 'root 1.1'],
                ['root 1', 'root 1.3'],
            ]);
            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: true,
                    fullPath: true,
                }),
            ).toEqual([
                ['root 1', 'root 1.2', 'root 1.2.2'],
                ['root 1', 'root 1.1'],
                ['root 1', 'root 1.3'],
            ]);
        });
    });

    describe('multi режим', () => {
        it('Корректно добавляет ноду', () => {
            const selectedItems: Path[] = [['root 1']];
            const nodesPath = [tree[0], tree[0].children![1]];

            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: false,
                    multi: true,
                }),
            ).toEqual([['root 1'], ['root 1', 'root 1.2']]);
            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: false,
                    multi: true,
                    fullPath: true,
                }),
            ).toEqual([['root 1'], ['root 1', 'root 1.2']]);
        });
        it('Корректно удаляет ноду', () => {
            const selectedItems: Path[] = [['root 1'], ['root 1', 'root 1.2']];
            const nodesPath = [tree[0]];

            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: false,
                    multi: true,
                }),
            ).toEqual([['root 1', 'root 1.2']]);

            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    checkable: false,
                    multi: true,
                    fullPath: true,
                }),
            ).toEqual([['root 1', 'root 1.2']]);
        });
    });

    describe('selectable режим', () => {
        it('Корректно выбирает ноду', () => {
            const selectedItems: Path[] = [['root 1']];
            const nodesPath = [tree[0], tree[0].children![1]];

            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                }),
            ).toEqual([['root 1', 'root 1.2']]);

            expect(
                getSelectItems({
                    selectedItems,
                    nodesPath,
                    fullPath: true,
                }),
            ).toEqual([['root 1', 'root 1.2']]);
        });
    });
});

describe('hasSelectedChildren', () => {
    const node = cloneDeep(viewTreeNode);

    it('Отсутствуют выбранные потомки', () => {
        const selectedItems: Path[] = [];
        expect(hasSelectedChildren(node, selectedItems)).toBeFalsy();
    });

    it('Содержит выбранных потомков', () => {
        const selectedItems: Path[] = [['parent', 'child2', 'child2.3', 'child2.3.1']];
        expect(hasSelectedChildren(node, selectedItems)).toBeTruthy();
    });
});

describe('flattenTree', () => {
    it('Создание плоского списка из дерева', () => {
        const tree = cloneDeep(viewTree);

        const result: FlatNode[] = [
            {treeNode: tree[0], padding: DEFAULT_PADDING_PX * 0, treeNodePath: [tree[0]]},
            {
                treeNode: tree[0].children![0],
                padding: DEFAULT_PADDING_PX * 1,
                treeNodePath: [tree[0], tree[0].children![0]],
            },
            {
                treeNode: tree[0].children![1],
                padding: DEFAULT_PADDING_PX * 1,
                treeNodePath: [tree[0], tree[0].children![1]],
            },
            {
                treeNode: tree[0].children![1].children![0],
                padding: DEFAULT_PADDING_PX * 2,
                treeNodePath: [tree[0], tree[0].children![1], tree[0].children![1].children![0]],
            },
            {
                treeNode: tree[0].children![2],
                padding: DEFAULT_PADDING_PX * 1,
                treeNodePath: [tree[0], tree[0].children![2]],
            },
            {treeNode: tree[1], padding: DEFAULT_PADDING_PX * 0, treeNodePath: [tree[1]]},
        ];

        expect(flattenTree(tree)).toEqual(result);
    });
});

describe('checkSelected', () => {
    const tree = cloneDeep(viewTree);

    it('Выбрана последная нода', () => {
        expect(
            checkSelected(tree[0].children![1].children![0], [['parent1', 'child2', 'child2.1']], false),
        ).toBeTruthy();
    });

    it('Не выбрана родительская нода с единственной выбранной последней нодой', () => {
        expect(checkSelected(tree[0].children![1].children![0], [['parent1', 'child2']], false)).toBeFalsy();
    });

    it('Выбрана сама нода для checkable режима', () => {
        expect(
            checkSelected(tree[0].children![1].children![0], [['parent1', 'child2', 'child2.1']], true),
        ).toBeTruthy();
    });

    it('Выбрана родитель ноды checkable режима', () => {
        expect(checkSelected(tree[0].children![1].children![0], [['parent1', 'child2']], true)).toBeTruthy();
        expect(checkSelected(tree[0].children![1].children![0], [['parent1']], true)).toBeTruthy();
    });

    it('Не выбрана сама нода или ее родители checkable режима', () => {
        expect(
            checkSelected(
                tree[0].children![1].children![0],
                [['parent2'], ['parent1', 'child3'], ['parent1', 'child1']],
                true,
            ),
        ).toBeFalsy();
    });
});

describe('getExpandedNodes', () => {
    const tree = cloneDeep(viewTree);

    it('Раскрытие ноды без детей', () => {
        expect(getExpandedNodes(tree[0].children![1].children![0], [])).toEqual([['parent1', 'child2', 'child2.1']]);
        expect(getExpandedNodes(tree[0].children![1].children![0], [['parent2']])).toEqual([
            ['parent2'],
            ['parent1', 'child2', 'child2.1'],
        ]);
    });

    it('Раскрытие ноды с детьми', () => {
        expect(getExpandedNodes(tree[0], [])).toEqual([['parent1']]);
        expect(getExpandedNodes(tree[0], [['parent2']])).toEqual([['parent2'], ['parent1']]);
    });

    it('Свертывание ноды без детей', () => {
        expect(getExpandedNodes(tree[0].children![1].children![0], [['parent1', 'child2', 'child2.1']])).toEqual([]);
        expect(
            getExpandedNodes(tree[0].children![1].children![0], [['parent1', 'child2', 'child2.1'], ['parent2']]),
        ).toEqual([['parent2']]);
    });

    it('Свертывание ноды с развернутыми детьми', () => {
        expect(
            getExpandedNodes(tree[0], [['parent1'], ['parent1', 'child2'], ['parent1', 'child2', 'child2.1']]),
        ).toEqual([]);
        expect(
            getExpandedNodes(tree[0], [
                ['parent1'],
                ['parent1', 'child2'],
                ['parent1', 'child2', 'child2.1'],
                ['parent2'],
            ]),
        ).toEqual([['parent2']]);
    });
});

describe('filterFlatTree', () => {
    const rawTree: SelectTreeNode[] = [
        {
            title: 'Корень 1',
            value: 'parent1',
            description: 'Описание корень 1',
            children: [
                {
                    title: 'Потомок 1',
                    value: 'child1',
                    description: 'Описание потомок 1 новомос',
                },
                {
                    title: 'Потомок 2',
                    value: 'child2',
                    description: 'Описание потомок 2 номос',
                    children: [{title: 'Ребенок', value: 'child2.1', description: 'Описание ребенок 1 мос'}],
                },
                {
                    title: 'Потомок 3',
                    value: 'child3',
                    description: 'Описание потомок 3',
                },
            ],
        },
        {title: 'Корень 2', value: 'parent2'},
    ];
    const tree = makeTreeDataFullPaths(rawTree);

    const PARENT_1 = {treeNode: tree[0], padding: DEFAULT_PADDING_PX * 0, treeNodePath: [tree[0]]};
    const PARENT_1_CHILD_1 = {
        treeNode: tree[0].children![0],
        padding: DEFAULT_PADDING_PX * 1,
        treeNodePath: [tree[0], tree[0].children![0]],
    };
    const PARENT_1_CHILD_2 = {
        treeNode: tree[0].children![1],
        padding: DEFAULT_PADDING_PX * 1,
        treeNodePath: [tree[0], tree[0].children![1]],
    };
    const PARENT_1_CHILD_2_CHILD_2_1 = {
        treeNode: tree[0].children![1].children![0],
        padding: DEFAULT_PADDING_PX * 2,
        treeNodePath: [tree[0], tree[0].children![1], tree[0].children![1].children![0]],
    };
    const PARENT_1_CHILD_3 = {
        treeNode: tree[0].children![2],
        padding: DEFAULT_PADDING_PX * 1,
        treeNodePath: [tree[0], tree[0].children![2]],
    };
    const PARENT_2 = {treeNode: tree[1], padding: DEFAULT_PADDING_PX * 0, treeNodePath: [tree[1]]};

    const flatTree: FlatNode[] = [
        PARENT_1,
        PARENT_1_CHILD_1,
        PARENT_1_CHILD_2,
        PARENT_1_CHILD_2_CHILD_2_1,
        PARENT_1_CHILD_3,
        PARENT_2,
    ];

    it('Корректно фильтрует по title', () => {
        expect(filterFlatTree(flatTree, [['parent1']], '')).toEqual([
            PARENT_1,
            PARENT_1_CHILD_1,
            PARENT_1_CHILD_2,
            PARENT_1_CHILD_3,
            PARENT_2,
        ]);

        expect(filterFlatTree(flatTree, [], 'кор')).toEqual([PARENT_2, PARENT_1]);
    });

    it('Корректно фильтрует по description', () => {
        expect(filterFlatTree(flatTree, [], 'потом')).toEqual([
            {...PARENT_1_CHILD_1, padding: DEFAULT_PADDING_PX * 0},
            {...PARENT_1_CHILD_2, padding: DEFAULT_PADDING_PX * 0},
            {...PARENT_1_CHILD_3, padding: DEFAULT_PADDING_PX * 0},
        ]);
    });

    it('Сортирует по признаку раннего вхождения', () => {
        expect(filterFlatTree(flatTree, [], 'мос')).toEqual([
            {...PARENT_1_CHILD_2_CHILD_2_1, padding: DEFAULT_PADDING_PX * 0},
            {...PARENT_1_CHILD_2, padding: DEFAULT_PADDING_PX * 0},
            {...PARENT_1_CHILD_1, padding: DEFAULT_PADDING_PX * 0},
        ]);
    });
});
