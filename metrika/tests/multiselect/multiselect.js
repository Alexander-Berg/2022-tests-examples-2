describe('multiselect', function () {
    var expect = chai.expect,
        blockName = 'multiselect',
        pathHash = BEM.blocks['multiselect-helpers'].pathHash,
        list = [
            {id: '0', title: 'item 0', path: ['0'], parent: 'root'},
            {id: '1', title: 'item 1', path: ['1'], parent: 'root', childs: [
                {id: 'child-0', title: 'child item 0', path: ['1', 'child-0'], parent: ['1']},
                {id: 'child-1', title: 'child item 1', path: ['1', 'child-1'], parent: ['1']},
                {id: 'child-2', title: 'child item 2', path: ['1', 'child-2'], parent: ['1']},
            ]},
        ],
        elem,
        block;

    beforeEach(function (done) {
        BEM.blocks['i-content'].html({
            block: blockName,
            list,
        }).then(function (html) {
            elem = $(html).appendTo('body');
            block = BEM.DOM.init(elem).bem(blockName);
            done();
        });
    });

    afterEach(function () {
        BEM.DOM.destruct(elem);
    });

    it('_generatePathMap create excess list with path IDs', function () {
        var pathKeyList = block._generatePathMap(list),
            listStub = {};

        listStub[pathHash(['0'])] = {id: '0', title: 'item 0', path: ['0'], parent: 'root'};
        listStub[pathHash(['1'])] = {id: '1', title: 'item 1', path: ['1'], parent: 'root', childs: [
            {id: 'child-0', title: 'child item 0', path: ['1', 'child-0'], parent: ['1']},
            {id: 'child-1', title: 'child item 1', path: ['1', 'child-1'], parent: ['1']},
            {id: 'child-2', title: 'child item 2', path: ['1', 'child-2'], parent: ['1']},
        ]};
        listStub[pathHash(['1', 'child-0'])] = {id: 'child-0', title: 'child item 0', path: ['1', 'child-0'], parent: ['1']};
        listStub[pathHash(['1', 'child-1'])] = {id: 'child-1', title: 'child item 1', path: ['1', 'child-1'], parent: ['1']};
        listStub[pathHash(['1', 'child-2'])] = {id: 'child-2', title: 'child item 2', path: ['1', 'child-2'], parent: ['1']};

        expect(pathKeyList).to.deep.equal(listStub);
    });

    describe('_getDiff', function () {
        it('find added root items at the end of new list', function () {
            var diff,
                newList = [
                    {id: '0', title: 'item 0', path: ['0'], parent: 'root'},
                    {id: '1', title: 'item 1', path: ['1'], parent: 'root', childs: [
                        {id: 'child-0', title: 'child item 0', path: ['1', 'child-0']},
                        {id: 'child-1', title: 'child item 1', path: ['1', 'child-1']},
                        {id: 'child-2', title: 'child item 2', path: ['1', 'child-2']},
                    ]},
                    {id: '3', title: 'item 0', path: ['3'], parent: 'root'},
                ],
                diffStub = {
                    'root': [
                        {id: '3', title: 'item 0', path: ['3'], parent: 'root'},
                    ],
                };

            diff = block._getDiff(list, newList);

            expect(diff.add).to.deep.equal(diffStub);
        });

        it('find added root items in the middle of new list', function () {
            var diff,
                newList = [
                    {id: '0', title: 'item 0', path: ['0'], parent: 'root'},
                    {id: '3', title: 'item 0', path: ['3'], parent: 'root'},
                    {id: '1', title: 'item 1', path: ['1'], parent: 'root', childs: [
                        {id: 'child-0', title: 'child item 0', path: ['1', 'child-0']},
                        {id: 'child-1', title: 'child item 1', path: ['1', 'child-1']},
                        {id: 'child-2', title: 'child item 2', path: ['1', 'child-2']},
                    ]},
                ],
                diffStub = {
                    'root': [
                        {id: '3', title: 'item 0', path: ['3'], parent: 'root'},
                    ],
                };

            diff = block._getDiff(list, newList);

            expect(diff.add).to.deep.equal(diffStub);
        });

        it('find added root items at the start of new list', function () {
            var diff,
                newList = [
                    {id: '3', title: 'item 0', path: ['3'], parent: 'root'},
                    {id: '0', title: 'item 0', path: ['0'], parent: 'root'},
                    {id: '1', title: 'item 1', path: ['1'], parent: 'root', childs: [
                        {id: 'child-0', title: 'child item 0', path: ['1', 'child-0']},
                        {id: 'child-1', title: 'child item 1', path: ['1', 'child-1']},
                        {id: 'child-2', title: 'child item 2', path: ['1', 'child-2']},
                    ]},
                ],
                diffStub = {
                    'root': [
                        {id: '3', title: 'item 0', path: ['3'], parent: 'root'},
                    ],
                };

            diff = block._getDiff(list, newList);

            expect(diff.add).to.deep.equal(diffStub);
        });

        it('find added child items', function () {
            var diff,
                newList = [
                    {id: '0', title: 'item 0', path: ['0']},
                    {id: '1', title: 'item 1', path: ['1'], childs: [
                        {id: 'child-0', title: 'child item 0', path: ['1', 'child-0'], parent: ['1']},
                        {id: 'child-1', title: 'child item 1', path: ['1', 'child-1'], parent: ['1']},
                        {id: 'child-2', title: 'child item 2', path: ['1', 'child-2'], parent: ['1']},
                        {id: 'child-3', title: 'child item 3', path: ['1', 'child-3'], parent: ['1']},
                        {id: 'child-4', title: 'child item 4', path: ['1', 'child-4'], parent: ['1']},
                    ]},
                ],
                diffStub = {};

            diffStub[['1']] = [
                {id: 'child-3', title: 'child item 3', path: ['1', 'child-3'], parent: ['1']},
                {id: 'child-4', title: 'child item 4', path: ['1', 'child-4'], parent: ['1']},
            ];

            diff = block._getDiff(list, newList);

            expect(diff.add).to.deep.equal(diffStub);
        });

        it('find added child items at the more deep levels', function () {
            var diff,
                newList = [
                    {id: '0', title: 'item 0', path: ['0'], parent: 'root'},
                    {id: '1', title: 'item 1', path: ['1'], parent: 'root', childs: [
                        {id: 'child-0', title: 'child item 0', path: ['1', 'child-0'], parent: ['1']},
                        {id: 'child-1', title: 'child item 1', path: ['1', 'child-1'], parent: ['1'], childs: [
                            {id: 'child-3', title: 'child item 3', path: ['1', 'child-1', 'child-3'], parent: ['1', 'child-1']},
                            {id: 'child-4', title: 'child item 4', path: ['1', 'child-1', 'child-4'], parent: ['1', 'child-1']},
                        ]},
                        {id: 'child-2', title: 'child item 2', path: ['1', 'child-2'], parent: ['1']},
                    ]},
                ],
                diffStub = {};

            diffStub[['1', 'child-1']] = [
                {id: 'child-3', title: 'child item 3', path: ['1', 'child-1', 'child-3'], parent: ['1', 'child-1']},
                {id: 'child-4', title: 'child item 4', path: ['1', 'child-1', 'child-4'], parent: ['1', 'child-1']},
            ];

            diff = block._getDiff(list, newList);

            expect(diff.add).to.deep.equal(diffStub);
        });

        it('should find changed paramValue or paramCondition', function () {
            var diff,
                newList = [
                    {id: '0', title: 'item 0', path: ['0'], paramCondition: '>', paramValue: '10'},
                    {id: '1', title: 'item 1', path: ['1'], childs: [
                        {id: 'child-0', title: 'child item 0', path: ['1', 'child-0']},
                        {id: 'child-1', title: 'child item 1', path: ['1', 'child-1'], paramCondition: '==', paramValue: '99'},
                        {id: 'child-2', title: 'child item 2', path: ['1', 'child-2']},
                    ]},
                ],
                diffStub = [
                    {id: '0', title: 'item 0', path: ['0'], paramCondition: '>', paramValue: '10'},
                    {id: 'child-1', title: 'child item 1', path: ['1', 'child-1'], paramCondition: '==', paramValue: '99'},
                ];

            diff = block._getDiff(list, newList);

            expect(diff.paramValue).to.deep.equal(diffStub);
        });
    });

    it('_renderNewItems append new childs to root', function () {
        var diff = {
                root: [
                {id: '5', title: 'item 5', path: ['5']},
                {id: '6', title: 'item 6', path: ['6']},
                ],
            },
            fakeItemsElem = {
                append: sinon.spy(),
            };

        block.renderHtml = sinon.spy();
        block.findElem = sinon.stub().returns(fakeItemsElem);
        block._renderNewItems(diff);

        expect(block.renderHtml.calledWith({
            block: 'multiselect',
            mods: block.getInitialMods(),
            elem: 'list-item',
            item: diff.root[0],
        })).to.be.true;
        expect(block.renderHtml.calledWith({
            block: 'multiselect',
            mods: block.getInitialMods(),
            elem: 'list-item',
            item: diff.root[1],
        })).to.be.true;
        expect(fakeItemsElem.append.called).to.be.true;
    });

});
