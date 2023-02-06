describe('i-filter-tree', function () {
    var expect = require('chai').expect,
        blockName = 'i-filter-tree',
        block;

    afterEach(function () {
        if (block) {
            block.destruct();
        }
    });

    describe('Filter constructor', function () {
        it('should accept empty value', function () {
            block = BEM.blocks[blockName].create('regionGeo', []);
            expect(block.get().values).to.deep.equal([]);
        });

        it('should accept simple-array single value', function () {
            block = BEM.blocks[blockName].create('regionGeo', [187, 20544, 143]);
            expect(block.get().values).to.deep.equal([{tree: [187, 20544, 143]}]);
        });

        it('should accept object value', function () {
            block = BEM.blocks[blockName].create('regionGeo', {tree: [187, 20544, 143]});
            expect(block.get().values).to.deep.equal([{tree: [187, 20544, 143]}]);
        });

        it('should accept array of simple-array values', function () {
            var r = [
                {tree: [187, 20544, 143]},
                {tree: [225, 1, 213]},
            ];

            block = BEM.blocks[blockName].create('regionGeo', [[187, 20544, 143], [225, 1, 213]]);
            expect(block.get().values).to.deep.equal(r);
        });

        it('should accept array of object values', function () {
            var r = [
                {tree: [187, 20544, 143]},
                {tree: [225, 1, 213]},
            ];

            block = BEM.blocks[blockName].create('regionGeo', [{tree: [187, 20544, 143]}, {tree: [225, 1, 213]}]);
            expect(block.get().values).to.deep.equal(r);
        });

        it('should accept tree with param value', function () {
            block = BEM.blocks[blockName].create('eventsTree', ['lookup', 'first', '#==10']);
            expect(block.get().values).to.deep.equal([{tree: ['lookup', 'first'], op: '==', val: '10'}]);
        });
    });

    describe('Filter operations', function () {
        it('should replace values', function () {
            block = BEM.blocks[blockName].create('regionGeo', [225, 1, 213]);

            block.replace([187, 20544, 143]);

            expect(block.get().values).to.deep.equal([{tree: [187, 20544, 143]}]);
        });

        it('should add values', function () {
            var r = [
                {tree: [187, 20544, 143]},
                {tree: [225, 1, 213]},
            ];

            block = BEM.blocks[blockName].create('regionGeo', [187, 20544, 143]);

            block.add([225, 1, 213]);

            expect(block.get().values).to.deep.equal(r);
        });

        it('should remove values', function () {
            block = BEM.blocks[blockName].create('regionGeo', [[187, 20544, 143], [225, 1, 213]]);

            block.remove([225, 1, 213]);

            expect(block.get().values).to.deep.equal([{tree: [187, 20544, 143]}]);
        });
    });

    describe('Filter serializer', function () {
        it('should serialize single value into AND-separeted values', function () {
            var r = '(ym:ge:regionCountry==187 AND ym:ge:regionArea==20544 AND ym:ge:regionCity==143)';

            block = BEM.blocks[blockName].create('regionGeo', [187, 20544, 143]);
            expect(block.serialize()).to.equal(r);
        });

        it('should serialize multiple values info OR separates strings', function () {
            var r = '((ym:ge:regionCountry==187 AND ym:ge:regionArea==20544 AND ym:ge:regionCity==143)' +
                ' OR (ym:ge:regionCountry==225 AND ym:ge:regionArea==1 AND ym:ge:regionCity==213))';

            block = BEM.blocks[blockName].create('regionGeo', [[187, 20544, 143], [225, 1, 213]]);
            expect(block.serialize()).to.equal(r);
        });
    });

    describe('Filter invert', function () {
        it('should invert AND-separeted serializer pattern', function () {
            var r = 'NOT (ym:ge:regionCountry==187 AND ym:ge:regionArea==20544 AND ym:ge:regionCity==143)';

            block = BEM.blocks[blockName].create('regionGeo', [187, 20544, 143], true);
            expect(block.serialize()).to.equal(r);
        });

        it('should invert OR separates strings pattern', function () {
            var r = 'NOT ((ym:ge:regionCountry==187 AND ym:ge:regionArea==20544 AND ym:ge:regionCity==143)' +
                ' OR (ym:ge:regionCountry==225 AND ym:ge:regionArea==1 AND ym:ge:regionCity==213))';

            block = BEM.blocks[blockName].create('regionGeo', [[187, 20544, 143], [225, 1, 213]], true);
            expect(block.serialize()).to.equal(r);
        });
    });

    describe('Filter special patterns', function () {
        it('eventsTree should use special pattern w/o paramValue', function () {
            var r = 'exists ym:ce:device with (ym:ce:paramsLevel1==\'first\' AND ym:ce:paramsLevel2==\'page\') AND ' +
                'ym:ce:eventLabel==\'lookup\'';

            block = BEM.blocks[blockName].create('eventsTree', ['lookup', 'first', 'page']);
            expect(block.serialize()).to.equal(r);
        });

        it('eventsTree should use special pattern with paramValue', function () {
            var r = 'exists ym:ce:device with (ym:ce:paramsLevel1==\'first\' AND ym:ce:paramsValueDouble==10) AND ' +
                'ym:ce:eventLabel==\'lookup\'';

            block = BEM.blocks[blockName].create('eventsTree', ['lookup', 'first', '==10']);
            expect(block.serialize()).to.equal(r);
        });

        it('eventsTree should use special pattern also when inverted', function () {
            var r = 'NOT (exists ym:ce:device with ' +
                '(ym:ce:paramsLevel1==\'first\' AND ym:ce:paramsLevel2==\'page\') AND ' +
                'ym:ce:eventLabel==\'lookup\')';

            block = BEM.blocks[blockName].create('eventsTree', ['lookup', 'first', 'page'], true);
            expect(block.serialize()).to.equal(r);
        });

        it('eventsTree should wraps all filter into exists with serialize flag', function () {
            var r = 'exists ym:ce:device with (ym:ce:paramsLevel1==\'first\' AND ' +
                'ym:ce:paramsValueDouble==10 AND ym:ce:eventLabel==\'lookup\')';

            block = BEM.blocks[blockName].create('eventsTree', ['lookup', 'first', '==10']);
            expect(block.serialize({wrapFullExists: true})).to.equal(r);
        });

        it('trackerParams should use special pattern in single-value input', function () {
            var r = 'exists ym:mc:device with (ym:mc:urlParamKey==\'geo\')';

            block = BEM.blocks[blockName].create('trackerParams', ['geo']);
            expect(block.serialize()).to.equal(r);
        });

        it('trackerParams should use special pattern', function () {
            var r = 'exists ym:mc:device with (ym:mc:urlParamKey==\'geo\' AND ym:mc:urlParamValue==\'ru\')';

            block = BEM.blocks[blockName].create('trackerParams', ['geo', 'ru']);
            expect(block.serialize()).to.equal(r);
        });
    });
});
