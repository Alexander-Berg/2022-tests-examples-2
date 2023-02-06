describe('filter-multiselect', function () {
    var expect = chai.expect,
        blockName = 'filter-multiselect',
        block;

    beforeEach(function () {
        block = BEM.DOM.create(blockName, {});
        block._model = BEM.blocks['m-filter-multiselect'].create();
        block.setStateModel(block._model);
        block.onStateChange = sinon.spy();
    });

    describe('_toggleItemSelected', function () {
        it('should add new filter value for simple filter', function (done) {
            var params = {
                    path: ['2'],
                },
                selected = true,
                initialState = {
                    filterValues: [
                        {op: '==', val: '0'},
                        {op: '==', val: '1'},
                    ],
                    isTreeFilter: false,
                    itemType: 'default',
                },
                resultValuesStub = [
                    {op: '==', val: '0'},
                    {op: '==', val: '1'},
                    {op: '==', val: '2'},
                ];

            block.setState(initialState)
            .then(function () {
                return block._toggleItemSelected(params, selected);
            })
            .then(function () {
                var state = block.getState();

                expect(state.filterValues).to.deep.equal(resultValuesStub);
                done();
            })
            .fail(function (e) {
                done(e);
            });
        });

        it('should remove filter value from simple filter', function (done) {
            var params = {
                    path: ['0'],
                },
                selected = false,
                initialState = {
                    filterValues: [
                        {op: '==', val: '0'},
                        {op: '==', val: '1'},
                    ],
                    isTreeFilter: false,
                    itemType: 'default',
                },
                resultValuesStub = [
                    {op: '==', val: '1'},
                ];

            block.setState(initialState)
            .then(function () {
                return block._toggleItemSelected(params, selected);
            })
            .then(function () {
                var state = block.getState();

                expect(state.filterValues).to.deep.equal(resultValuesStub);
                done();
            })
            .fail(function (e) {
                done(e);
            });
        });

        it('should add filter value for tree filter', function (done) {
            var params = {
                    path: ['4', '5'],
                },
                selected = true,
                initialState = {
                    filterValues: [
                        {
                            tree: ['0', '1'],
                        },
                        {
                            tree: ['2', '3'],
                        },
                    ],
                    isTreeFilter: true,
                    itemType: 'default',
                },
                resultValuesStub = [
                    {
                        tree: ['0', '1'],
                    },
                    {
                        tree: ['2', '3'],
                    },
                    {
                        tree: ['4', '5'],
                    },
                ];

            block.setState(initialState)
            .then(function () {
                return block._toggleItemSelected(params, selected);
            })
            .then(function () {
                var state = block.getState();

                expect(state.filterValues).to.deep.equal(resultValuesStub);
                done();
            })
            .fail(function (e) {
                done(e);
            });
        });

        it('should remove filter value for tree filter', function (done) {
            var params = {
                    path: ['0', '1'],
                },
                selected = false,
                initialState = {
                    filterValues: [
                        {
                            tree: ['0', '1'],
                        },
                        {
                            tree: ['2', '3'],
                        },
                    ],
                    isTreeFilter: true,
                    itemType: 'default',
                },
                resultValuesStub = [
                    {
                        tree: ['2', '3'],
                    },
                ];

            block.setState(initialState)
            .then(function () {
                return block._toggleItemSelected(params, selected);
            })
            .then(function () {
                var state = block.getState();

                expect(state.filterValues).to.deep.equal(resultValuesStub);
                done();
            })
            .fail(function (e) {
                done(e);
            });
        });
    });

});
