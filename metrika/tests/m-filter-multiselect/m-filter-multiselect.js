describe('m-filter-multiselect', function () {
    var expect = chai.expect,
        blockName = 'm-filter-multiselect',
        block,
        list = [
            {id: '0', title: 'item bar 0', path: ['0'], childs: [
                {id: 'child0', title: 'item bar 0', path: ['0', 'child0']},
            ]},
            {id: '1', title: 'item foo 1', path: ['1']},
        ];

    beforeEach(function () {
        block = BEM.blocks[blockName].create();
    });

    afterEach(function () {
        block.destruct();
    });

    describe('filterListByPhrase', function () {
        it('should not mutate initial list', function () {
            var state = {
                    list,
                    searchPhrase: 'bar',
                },
                originalList = _.cloneDeep(state.list);

            block.filterListByPhrase(state.list, state.searchPhrase);
            expect(state.list).to.deep.equal(originalList);
        });

        it('filter list by phrase', function () {
            var state = {
                    list,
                    searchPhrase: 'bar',
                },
                filteredStub = [
                    {id: '0', title: 'item bar 0', path: ['0'], childs: [
                        {id: 'child0', title: 'item bar 0', path: ['0', 'child0']},
                    ]},
                ],
                filtered;

            filtered = block.filterListByPhrase(state.list, state.searchPhrase);
            expect(filtered).to.deep.equal(filteredStub);
        });
    });

    describe('toggleLoadMore', function () {
        var list = [
            {id: '0', title: 'item bar 0', path: ['0'], childs: [
                {id: 'child0', title: 'child 0', path: ['0', 'child0'], total: 10, childs: [
                    {id: 'child1', title: 'child 1', path: ['0', 'child0', 'child1']},
                ]},
            ]},
            {id: '1', title: 'item foo 1', path: ['1'], total: 20, childs: []},
        ];

        it('should not mutate original state', function () {
            var state = {
                    list,
                },
                originalState = _.cloneDeep(state);

            block.toggleLoadMore(state);
            expect(state).to.deep.equal(originalState);
        });

        it('should set \'loadMore\' attribute to items where total > childs lengs', function () {
            var state = {
                list,
                total: 25,
            };

            state = block.toggleLoadMore(state);
            expect(state.loadMore, 'root state does not have loadMore').to.be.true;
            expect(state.list[0].childs[0].loadMore).to.be.true;
        });
    });

    describe('selectFilterValues', function () {
        it('should not mutate original list', function () {
            var listClone = _.cloneDeep(list),
                filterValues = [
                    {tree: ['1']},
                    {tree: ['0', 'child0']},
                ],
                isTreeFilter = true,
                isMultidimFilter = false;

            block.selectFilterValues(list, filterValues, isTreeFilter, isMultidimFilter);
            expect(list).to.deep.equal(listClone);
        });

        it('should select items for tree filter', function () {
            var filterValues = [
                    {tree: ['1']},
                    {tree: ['0', 'child0']},
                ],
                selected,
                isTreeFilter = true,
                isMultidimFilter = false;

            selected = block.selectFilterValues(list, filterValues, isTreeFilter, isMultidimFilter);
            expect(selected[1].selected).to.be.true;
            expect(selected[0].childs[0].selected).to.be.true;
        });

        it('should set param value to tree items', function () {
            var filterValues = [
                    {tree: ['1'], op: '==', val: '23'},
                    {tree: ['0', 'child0'], op: '>', val: '100'},
                ],
                selected,
                isTreeFilter = true,
                isMultidimFilter = false;

            selected = block.selectFilterValues(list, filterValues, isTreeFilter, isMultidimFilter);
            expect(selected[1].paramCondition).to.equal('==');
            expect(selected[1].paramValue).to.equal('23');
            expect(selected[0].childs[0].paramCondition).to.equal('>');
            expect(selected[0].childs[0].paramValue).to.equal('100');
        });

        it('should select simple values', function () {
            var filterValues = [
                    {op: '==', val: '0'},
                    {op: '==', val: '1'},
                ],
                selected,
                isTreeFilter = false,
                isMultidimFilter = false;

            selected = block.selectFilterValues(list, filterValues, isTreeFilter, isMultidimFilter);
            expect(selected[0].selected).to.be.true;
            expect(selected[1].selected).to.be.true;
        });

        it('should select multidimensional values', function () {
            var list = [
                    {id: 'foo#bar', title: 'item bar 0', path: ['foo#bar']},
                    {id: 'bar#baz', title: 'item foo 1', path: ['bar#baz']},
                ],
                filterValues = [
                    {op: '==', val: ['bar', 'baz']},
                ],
                selected,
                isTreeFilter = false,
                isMultidimFilter = true;

            selected = block.selectFilterValues(list, filterValues, isTreeFilter, isMultidimFilter);
            expect(selected[1].selected).to.be.true;
        });
    });

    describe('toggleItem', function () {
        it('should not mutate original values array', function () {
            var filterValues = [
                    {op: '==', val: '1'},
                    {op: '==', val: '2'},
                    {op: '==', val: '3'},
                    {op: '==', val: '4'},
                ],
                filterValuesClone = _.cloneDeep(filterValues),
                state = {
                    filterValues,
                    isTreeFilter: false,
                    isMultidimFilter: false,
                };

            block.toggleItem(state, ['5'], true);
            expect(filterValues).to.deep.equal(filterValuesClone);
        });

        it('should add simple item to values array', function () {
            var filterValues = [
                    {op: '==', val: '1'},
                    {op: '==', val: '2'},
                    {op: '==', val: '3'},
                    {op: '==', val: '4'},
                ],
                valuePath = ['5'],
                toggledStub = [
                    {op: '==', val: '1'},
                    {op: '==', val: '2'},
                    {op: '==', val: '3'},
                    {op: '==', val: '4'},
                    {op: '==', val: '5'},
                ],
                state = {
                    filterValues,
                    isTreeFilter: false,
                    isMultidimFilter: false,
                },
                toggledValues;

            toggledValues = block.toggleItem(state, valuePath, true);
            expect(toggledValues).to.deep.equal(toggledStub);
        });

        it('should add tree item to values array', function () {
            var filterValues = [
                    {tree: ['1', '2', '3', '4']},
                    {tree: ['1', '2']},
                ],
                selectedValue = ['5', '6', '7'],
                toggledStub = [
                    {tree: ['1', '2', '3', '4']},
                    {tree: ['1', '2']},
                    {tree: ['5', '6', '7']},
                ],
                state = {
                    filterValues,
                    isTreeFilter: true,
                    isMultidimFilter: false,
                },
                toggledValues;

            toggledValues = block.toggleItem(state, selectedValue, true);
            expect(toggledValues).to.deep.equal(toggledStub);
        });

        it('should remove simple item from values array', function () {
            var filterValues = [
                    {op: '==', val: '1'},
                    {op: '==', val: '2'},
                    {op: '==', val: '3'},
                    {op: '==', val: '4'},
                ],
                removedValue = ['2'],
                toggledStub = [
                    {op: '==', val: '1'},
                    {op: '==', val: '3'},
                    {op: '==', val: '4'},
                ],
                state = {
                    filterValues,
                    isTreeFilter: false,
                    isMultidimFilter: false,
                },
                toggledValues;

            toggledValues = block.toggleItem(state, removedValue, false);
            expect(toggledValues).to.deep.equal(toggledStub);
        });

        it('should remove tree item from values array', function () {
            var filterValues = [
                    {tree: ['1', '2', '3', '4']},
                    {tree: ['1', '8']},
                    {tree: ['5', '6', '7']},
                ],
                removedValue = ['1', '8'],
                toggledStub = [
                    {tree: ['1', '2', '3', '4']},
                    {tree: ['5', '6', '7']},
                ],
                state = {
                    filterValues,
                    isTreeFilter: true,
                    isMultidimFilter: false,
                },
                toggledValues;

            toggledValues = block.toggleItem(state, removedValue, false);
            expect(toggledValues).to.deep.equal(toggledStub);
        });

        it('should remove nested tree item of selected upper item', function () {
            var filterValues = [
                    {tree: ['1', '2', '3', '4']},
                    {tree: ['1', '5']},
                ],
                selectedValue = ['1', '2'],
                toggledStub = [
                    {tree: ['1', '5']},
                    {tree: ['1', '2']},
                ],
                state = {
                    filterValues,
                    isTreeFilter: true,
                    isMultidimFilter: false,
                },
                toggledValues;

            toggledValues = block.toggleItem(state, selectedValue, true);
            expect(toggledValues).to.deep.equal(toggledStub);
        });

        it('should remove parent tree item of selected item', function () {
            var filterValues = [
                    {tree: ['1', '2']},
                    {tree: ['1', '5']},
                ],
                selectedValue = ['1', '2', '3'],
                toggledStub = [
                    {tree: ['1', '5']},
                    {tree: ['1', '2', '3']},
                ],
                state = {
                    filterValues,
                    isTreeFilter: true,
                    isMultidimFilter: false,
                },
                toggledValues;

            toggledValues = block.toggleItem(state, selectedValue, true);
            expect(toggledValues).to.deep.equal(toggledStub);
        });

        it('should add multidimensional value to filter values array', function () {
            var filterValues = [
                    {op: '==', val: ['1', '2']},
                    {op: '==', val: ['3', '4']},
                ],
                addValue = ['foo#bar'],
                toggledStub = [
                    {op: '==', val: ['1', '2']},
                    {op: '==', val: ['3', '4']},
                    {op: '==', val: ['foo', 'bar']},
                ],
                state = {
                    filterValues,
                    isTreeFilter: false,
                    isMultidimFilter: true,
                },
                selected = true,
                toggledValues;

            toggledValues = block.toggleItem(state, addValue, selected);
            expect(toggledValues).to.deep.equal(toggledStub);
        });

        it('should remove multidimensional value from filter values array', function () {
            var filterValues = [
                    {op: '==', val: ['1', '2']},
                    {op: '==', val: ['foo', 'bar']},
                    {op: '==', val: ['3', '4']},
                ],
                removeValue = ['foo#bar'],
                toggledStub = [
                    {op: '==', val: ['1', '2']},
                    {op: '==', val: ['3', '4']},
                ],
                state = {
                    filterValues,
                    isTreeFilter: false,
                    isMultidimFilter: true,
                },
                selected = false,
                toggledValues;

            toggledValues = block.toggleItem(state, removeValue, selected);
            expect(toggledValues).to.deep.equal(toggledStub);
        });
    });

    describe('setParamValue', function () {
        it('should not mutate original values array', function () {
            var filterValues = [
                    {op: '==', val: '1'},
                    {op: '==', val: '2'},
                    {op: '==', val: '3'},
                    {op: '==', val: '4'},
                ],
                filterValuesClone = _.cloneDeep(filterValues),
                state = {
                    filterValues,
                    isTreeFilter: true,
                },
                param = {
                    paramCondition: 'less',
                    paramValue: 10,
                };

            block.setParamValue(state, ['1', '2'], param);
            expect(filterValues).to.deep.equal(filterValuesClone);
        });

        it('should set param value for tree item', function () {
            var filterValues = [
                    {tree: ['1', '2', '3', '4']},
                    {tree: ['1', '2']},
                ],
                state = {
                    filterValues,
                    isTreeFilter: true,
                },
                param = {
                    paramCondition: '>',
                    paramValue: 10,
                },
                updated;

            updated = block.setParamValue(state, ['1', '2'], param);
            expect(updated[1].op).to.equal('>');
            expect(updated[1].val).to.equal(10);
        });

        it('should do nothing for simple item', function () {
            var filterValues = [
                    {op: '==', val: '1'},
                    {op: '==', val: '2'},
                    {op: '==', val: '3'},
                    {op: '==', val: '4'},
                ],
                state = {
                    filterValues,
                    isTreeFilter: false,
                },
                param = {
                    paramCondition: '>',
                    paramValue: 10,
                },
                updated;

            updated = block.setParamValue(state, ['2'], param);
            expect(updated).to.deep.equal(filterValues);
        });
    });

    describe('generateNotLoadedItems', function () {
        it('should not mutate original list', function () {
            var state = {
                    filterValues: [
                        {op: '==', val: '3'},
                    ],
                    isTreeFilter: false,
                },
                listClone = _.cloneDeep(list);

            block.generateNotLoadedItems(list, state);
            expect(list).to.deep.equal(listClone);
        });

        it('should generate item for non-tree filters', function () {
            var state = {
                    filterValues: [
                        {op: '==', val: '3'},
                        {op: '==', val: '4'},
                    ],
                    isTreeFilter: false,
                },
                updatedStub = [
                    {id: '4', title: '4', path: ['4'], parent: 'root', expand: false, childs: []},
                    {id: '3', title: '3', path: ['3'], parent: 'root', expand: false, childs: []},
                    {id: '0', title: 'item bar 0', path: ['0'], childs: [
                        {id: 'child0', title: 'item bar 0', path: ['0', 'child0']},
                    ]},
                    {id: '1', title: 'item foo 1', path: ['1']},
                ],
                updated;

            updated = block.generateNotLoadedItems(list, state);
            expect(updated).to.deep.equal(updatedStub);
        });

        it('should generate 1-level item for tree filters', function () {
            var state = {
                    filterValues: [
                        {tree: ['3']},
                        {tree: ['4']},
                    ],
                    isTreeFilter: true,
                },
                updatedStub = [
                    {id: '4', title: '4', path: ['4'], parent: 'root', expand: false, childs: []},
                    {id: '3', title: '3', path: ['3'], parent: 'root', expand: false, childs: []},
                    {id: '0', title: 'item bar 0', path: ['0'], childs: [
                        {id: 'child0', title: 'item bar 0', path: ['0', 'child0']},
                    ]},
                    {id: '1', title: 'item foo 1', path: ['1']},
                ],
                updated;

            updated = block.generateNotLoadedItems(list, state);
            expect(updated).to.deep.equal(updatedStub);
        });

        it('should extend 1-level items with generated nested nodes if 1-level item is expanded', function () {
            var state = {
                    filterValues: [
                        {tree: ['1', 'child1']},
                    ],
                    isTreeFilter: true,
                },
                list = [
                    {id: '0', title: '0', path: ['0'], childs: [
                        {id: 'child0', title: 'item bar 0', path: ['0', 'child0']},
                    ]},
                    {id: '1', title: '1', path: ['1'], expand: true, expanded: true},
                ],
                updatedStub = [
                    {id: '0', title: '0', path: ['0'], childs: [
                        {id: 'child0', title: 'item bar 0', path: ['0', 'child0']},
                    ]},
                    {id: '1', title: '1', path: ['1'], expand: true, expanded: true, parent: 'root', childs: [
                        {id: 'child1', title: 'child1', path: ['1', 'child1'], parent: ['1'], expand: false, childs: []},
                    ]},
                ],
                updated;

            updated = block.generateNotLoadedItems(list, state);
            expect(updated).to.deep.equal(updatedStub);
        });

        it('should extend 1-level items with generated nested nodes but remain original title', function () {
            var state = {
                    filterValues: [
                        {tree: ['1', 'child1']},
                    ],
                    isTreeFilter: true,
                },
                list = [
                    {id: '0', title: 'item bar 0', path: ['0'], childs: [
                        {id: 'child0', title: 'item bar 0', path: ['0', 'child0']},
                    ]},
                    {id: '1', title: 'REMAIN TITLE', path: ['1'], expand: true, expanded: true},
                ],
                updatedStub = [
                    {id: '0', title: 'item bar 0', path: ['0'], childs: [
                        {id: 'child0', title: 'item bar 0', path: ['0', 'child0']},
                    ]},
                    {id: '1', title: 'REMAIN TITLE', path: ['1'], expand: true, expanded: true, parent: 'root', childs: [
                        {id: 'child1', title: 'child1', path: ['1', 'child1'], parent: ['1'], expand: false, childs: []},
                    ]},
                ],
                updated;

            updated = block.generateNotLoadedItems(list, state);
            expect(updated).to.deep.equal(updatedStub);
        });

        it('should NOT extend 1-level items when sub-nodes already in list', function () {
            var state = {
                    filterValues: [
                        {tree: ['0', 'child0']},
                    ],
                    isTreeFilter: true,
                },
                list = [
                    {id: '0', title: 'item bar 0', path: ['0'], childs: [
                        {id: 'child0', title: 'item bar 0', path: ['0', 'child0']},
                    ]},
                    {id: '1', title: 'item foo 1', path: ['1']},
                ],
                updatedStub = _.cloneDeep(list),
                updated;

            updated = block.generateNotLoadedItems(list, state);
            expect(updated).to.deep.equal(updatedStub);
        });

        it('should extend non 1-level items with generated nested nodes', function () {
            var state = {
                    filterValues: [
                        {tree: ['0', 'child0', 'child1']},
                    ],
                    isTreeFilter: true,
                },
                list = [
                    {id: '0', title: 'REMAIN TITLE', path: ['0'], expand: true, expanded: true, childs: [
                        {id: 'child0', title: 'REMAIN CHILD TITLE', path: ['0', 'child0'], expand: true, expanded: true},
                    ]},
                    {id: '1', title: 'item foo 1', path: ['1']},
                ],
                updatedStub = [
                    {id: '0', title: 'REMAIN TITLE', path: ['0'], parent: 'root', expand: true, expanded: true, childs: [
                        {id: 'child0', title: 'REMAIN CHILD TITLE', path: ['0', 'child0'],
                            expand: true,
                            expanded: true,
                            parent: ['0'],
                            childs: [
                                {id: 'child1', title: 'child1', path: ['0', 'child0', 'child1'],
                                    childs: [],
                                    parent: ['0', 'child0'],
                                    expand: false,
                                },
                            ]},
                    ]},
                    {id: '1', title: 'item foo 1', path: ['1']},
                ],
                updated;

            updated = block.generateNotLoadedItems(list, state);
            expect(updated).to.deep.equal(updatedStub);
        });

        it('should NOT generate duplicates of existing first level items', function () {
            var list = [
                {id: '0', title: 'item bar 0', path: ['0'], childs: [
                        {id: 'child0', title: 'item bar 0', path: ['0', 'child0']},
                ]},
                    {id: '1', title: 'item foo 1', path: ['1'], expand: true},
                ],
                filterValues = [
                    {tree: ['1', 'child0']},
                ],
                isTreeFilter = true,
                updated;

            updated = block.generateNotLoadedItems(list, filterValues, isTreeFilter);
            expect(updated).to.deep.equal(list);
        });

        it('should NOT generate new items for existing multidimensional values', function () {
            var state = {
                    filterValues: [
                        {op: '==', val: ['bar', 'baz']},
                    ],
                    isTreeFilter: false,
                    isMultidimFilter: true,
                },
                list = [
                    {id: 'foo#bar', title: 'item bar 0', path: ['foo#bar']},
                    {id: 'bar#baz', title: 'item foo 1', path: ['bar#baz']},
                ],
                updated;

            updated = block.generateNotLoadedItems(list, state);
            expect(updated).to.deep.equal(list);
        });
    });

    describe('orderItems', function () {
        it('should move selected 1-level items up to the list', function () {
            var list = [
                    {id: '4', title: '4', path: ['4']},
                    {id: '3', title: '3', path: ['3'], selected: true},
                {id: '0', title: 'item bar 0', path: ['0'], indeterminate: true, childs: [
                        {id: 'child0', title: 'item bar 0', path: ['0', 'child0'], selected: true},
                ]},
                    {id: '1', title: 'item foo 1', path: ['1']},
                ],
                defaultList = [],
                orderedStub = [
                    {id: '3', title: '3', path: ['3'], selected: true},
                    {id: '0', title: 'item bar 0', path: ['0'], indeterminate: true, childs: [
                        {id: 'child0', title: 'item bar 0', path: ['0', 'child0'], selected: true},
                    ]},
                    {id: '4', title: '4', path: ['4']},
                    {id: '1', title: 'item foo 1', path: ['1']},
                ],
                ordered;

            ordered = block.orderItems(list, defaultList);
            expect(ordered).to.deep.equal(orderedStub);
        });

        it('should move default list item on tom of the list and on top of selected items', function () {
            var list = [
                    {id: '4', title: '4', path: ['4']},
                    {id: '3', title: '3', path: ['3'], selected: true},
                {id: '0', title: 'item bar 0', path: ['0'], indeterminate: true, childs: [
                        {id: 'child0', title: 'item bar 0', path: ['0', 'child0'], selected: true},
                ]},
                    {id: 'default1', title: 'default 1', path: ['default1']},
                    {id: 'default2', title: 'default 2', path: ['default2']},
                    {id: '1', title: 'item foo 1', path: ['1']},
                ],
                defaultList = [
                    {id: 'default1', title: 'default 1', path: ['default1']},
                    {id: 'default2', title: 'default 2', path: ['default2']},
                ],
                orderedStub = [
                    {id: 'default1', title: 'default 1', path: ['default1']},
                    {id: 'default2', title: 'default 2', path: ['default2']},
                    {id: '3', title: '3', path: ['3'], selected: true},
                    {id: '0', title: 'item bar 0', path: ['0'], indeterminate: true, childs: [
                        {id: 'child0', title: 'item bar 0', path: ['0', 'child0'], selected: true},
                    ]},
                    {id: '4', title: '4', path: ['4']},
                    {id: '1', title: 'item foo 1', path: ['1']},
                ],
                ordered;

            ordered = block.orderItems(list, defaultList);
            expect(ordered).to.deep.equal(orderedStub);
        });
    });

});
