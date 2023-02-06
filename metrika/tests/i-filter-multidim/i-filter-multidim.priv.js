describe('i-filter-multidim', function () {
    var expect = require('chai').expect,
        blockName = 'i-filter-multidim',
        block;

    afterEach(function () {
        if (block) {
            block.destruct();
        }
    });

    describe('Filter constructor', function () {
        it('should accept empty value', function () {
            block = BEM.blocks[blockName].create('appVersion', []);
            expect(block.get().values).to.deep.equal([]);
        });

        it('should accept simple single value', function () {
            block = BEM.blocks[blockName].create('appVersion', ['1.8', 'android']);
            expect(block.get().values).to.deep.equal([{op: '==', val: ['1.8', 'android']}]);
        });

        it('should accept array of simple value', function () {
            block = BEM.blocks[blockName].create('appVersion', [['1.8', 'android'], ['2.0', 'iOS']]);
            expect(block.get().values).to.deep.equal([
                {op: '==', val: ['1.8', 'android']},
                {op: '==', val: ['2.0', 'iOS']},
            ]);
        });

        it('should accept string value', function () {
            block = BEM.blocks[blockName].create('appVersion', '1.8#android');
            expect(block.get().values).to.deep.equal([{op: '==', val: ['1.8', 'android']}]);
        });

        it('should accept array of string values', function () {
            block = BEM.blocks[blockName].create('appVersion', ['1.8#android', '2.0#iOS']);
            expect(block.get().values).to.deep.equal([
                {op: '==', val: ['1.8', 'android']},
                {op: '==', val: ['2.0', 'iOS']},
            ]);
        });

        it('should accept null values', function () {
            block = BEM.blocks[blockName].create('appVersion', [null, null]);
            expect(block.get().values).to.deep.equal([{op: '==', val: [null, null]}]);
        });

        it('should not accept unknown filter', function () {
            expect(BEM.blocks[blockName].create.bind(BEM.blocks[blockName], 'qwerty', 1)).to.throw(Error);
        });

        it('should handle full object value', function () {
            var values = [
                {op: '==', val: ['1.5.5644.43', 'WindowsPhone']},
                {op: '==', val: ['1.3.5424.53', 'WindowsPhone']},
            ];

            block = BEM.blocks[blockName].create('appVersion', values);
            expect(block.get().values).to.deep.equal(values);
        });
    });

    describe('Filter operations', function () {
        it('should replace values', function () {
            block = BEM.blocks[blockName].create('appVersion', ['1.8#android', '2.0#iOS']);

            block.replace('3.14#WinPhone');

            expect(block.get().values).to.deep.equal([{op: '==', val: ['3.14', 'WinPhone']}]);
        });

        it('should add values', function () {
            block = BEM.blocks[blockName].create('appVersion', ['1.8#android', '2.0#iOS']);

            block.add('3.14#WinPhone');

            expect(block.get().values).to.deep.equal([
                {op: '==', val: ['1.8', 'android']},
                {op: '==', val: ['2.0', 'iOS']},
                {op: '==', val: ['3.14', 'WinPhone']},
            ]);
        });

        it('should remove values', function () {
            block = BEM.blocks[blockName].create('appVersion', ['1.8#android', '2.0#iOS', '3.14#WinPhone']);

            block.remove('3.14#WinPhone');

            expect(block.get().values).to.deep.equal([
                {op: '==', val: ['1.8', 'android']},
                {op: '==', val: ['2.0', 'iOS']},
            ]);
        });
    });

    describe('Filter serializer', function () {
        it('should serialize into OR pattern', function () {
            var r = '((ym:ge:appVersion==\'1.8\' AND ym:ge:operatingSystem==\'android\') OR ' +
                '(ym:ge:appVersion==\'2.0\' AND ym:ge:operatingSystem==\'iOS\'))';

            block = BEM.blocks[blockName].create('appVersion', ['1.8#android', '2.0#iOS']);
            expect(block.serialize()).to.equal(r);
        });

        it('should serialize into inverted OR pattern', function () {
            var r = 'NOT ((ym:ge:appVersion==\'1.8\' AND ym:ge:operatingSystem==\'android\') OR ' +
                '(ym:ge:appVersion==\'2.0\' AND ym:ge:operatingSystem==\'iOS\'))';

            block = BEM.blocks[blockName].create('appVersion', ['1.8#android', '2.0#iOS'], true);
            expect(block.serialize()).to.equal(r);
        });

        it('should use ns from params', function () {
            var r = '(ym:ce:appVersion==\'1.8\' AND ym:ce:operatingSystem==\'android\')';

            block = BEM.blocks[blockName].create('appVersion', '1.8#android');
            expect(block.serialize({ns: 'ce'})).to.equal(r);
        });

        it('should propertly serialize null\'s', function () {
            var r = '(ym:ge:appVersion==null AND ym:ge:operatingSystem==null)';

            block = BEM.blocks[blockName].create('appVersion', 'null#null');
            expect(block.serialize()).to.equal(r);
        });
    });
});
