describe('i-filter-simple', function () {
    var expect = require('chai').expect,
        blockName = 'i-filter-simple',
        block;

    afterEach(function () {
        if (block) {
            block.destruct();
        }
    });

    describe('Filter constructor', function () {
        it('should accept empty value', function () {
            block = BEM.blocks[blockName].create('city', []);
            expect(block.get().values).to.deep.equal([]);
        });

        it('should accept undefined value', function () {
            block = BEM.blocks[blockName].create('city', undefined);
            expect(block.get().values).to.deep.equal([]);
        });

        it('should accept simple single value', function () {
            block = BEM.blocks[blockName].create('city', 1);
            expect(block.get().values).to.deep.equal([{op: '==', val: '1'}]);
        });

        it('should accept array of simple value', function () {
            block = BEM.blocks[blockName].create('city', [1, 2, 3]);
            expect(block.get().values).to.deep.equal([{op: '==', val: '1'}, {op: '==', val: '2'}, {op: '==', val: '3'}]);
        });

        it('should accept string value', function () {
            block = BEM.blocks[blockName].create('city', '>1');
            expect(block.get().values).to.deep.equal([{op: '>', val: '1'}]);
        });

        it('should accept array of string values', function () {
            block = BEM.blocks[blockName].create('city', ['>1', '<2', '==3']);
            expect(block.get().values).to.deep.equal([{op: '>', val: '1'}, {op: '<', val: '2'}, {op: '==', val: '3'}]);
        });

        it('should accept object value', function () {
            block = BEM.blocks[blockName].create('city', {op: '>', val: '1'});
            expect(block.get().values).to.deep.equal([{op: '>', val: '1'}]);
        });

        it('should accept array of object values', function () {
            block = BEM.blocks[blockName].create('city', [
                {op: '>', val: '1'},
                {op: '<', val: '2'},
                {op: '==', val: '3'},
            ]);
            expect(block.get().values).to.deep.equal([{op: '>', val: '1'}, {op: '<', val: '2'}, {op: '==', val: '3'}]);
        });

        it('should not accept unknown filter', function () {
            expect(BEM.blocks[blockName].create.bind(BEM.blocks[blockName], 'qwerty', 1)).to.throw(Error);
        });
    });

    describe('Filter operations', function () {
        it('should replace values', function () {
            block = BEM.blocks[blockName].create('city', [
                {op: '>', val: '1'},
                {op: '<', val: '2'},
            ]);

            block.replace({op: '==', val: '3'});

            expect(block.get().values).to.deep.equal([{op: '==', val: '3'}]);
        });

        it('should add values', function () {
            block = BEM.blocks[blockName].create('city', [
                {op: '>', val: '1'},
                {op: '<', val: '2'},
            ]);

            block.add({op: '==', val: '3'});

            expect(block.get().values).to.deep.equal([{op: '>', val: '1'}, {op: '<', val: '2'}, {op: '==', val: '3'}]);
        });

        it('should remove values', function () {
            block = BEM.blocks[blockName].create('city', [
                {op: '>', val: '1'},
                {op: '<', val: '2'},
            ]);

            block.remove({op: '<', val: '2'});

            expect(block.get().values).to.deep.equal([{op: '>', val: '1'}]);
        });
    });

    describe('Filter serializer', function () {
        it('should serialize single char operator', function () {
            var r = 'ym:ge:regionCity!n';

            block = BEM.blocks[blockName].create('city', {op: '!n', val: ''});
            expect(block.serialize()).to.equal(r);
        });

        it('should serialize into IN pattern', function () {
            var r = 'ym:ge:regionCity IN (1,2,3)';

            block = BEM.blocks[blockName].create('city', [1, 2, 3]);
            expect(block.serialize()).to.equal(r);
        });

        it('should NOT serialize \'afterInstallEvent\' into IN pattern', function () {
            var r = '(ym:ge:afterInstallEventName==\'OFFLINE_SYNC\' OR ' +
                'ym:ge:afterInstallEventName==\'PHOTOSLICE_SYNC\')';

            block = BEM.blocks[blockName].create('afterInstallEvent', ['OFFLINE_SYNC', 'PHOTOSLICE_SYNC']);
            expect(block.serialize()).to.equal(r);
        });

        it('should NOT make double inverted filter with special pattern', function () {
            var r = 'ym:s:sessionTimeInterval NOT IN (10,1)';

            block = BEM.blocks[blockName].create('sessionInterval', [10, 1]);
            expect(block.setInverted(true).serialize()).to.equal(r);
        });

        it('should use internal pattern', function () {
            var r = 'exists ym:ge:device, ym:ge:specialDefaultDate with (ym:ge:eventType==\'EVENT_INIT\')';

            block = BEM.blocks[blockName].create('newUsers', {op: '==', val: 1});
            expect(block.serialize()).to.equal(r);
        });

        it('should use ns from params', function () {
            var r = 'exists ym:ce:device, ym:ce:specialDefaultDate with (ym:ce:eventType==\'EVENT_INIT\')';

            block = BEM.blocks[blockName].create('newUsers', {op: '==', val: 1});
            expect(block.serialize({ns: 'ce'})).to.equal(r);
        });

        it('should be quoted if required in filter def', function () {
            var r = 'ym:ge:locale IN (\'ru\',\'en\',\'123\',\'3.14\')';

            block = BEM.blocks[blockName].create('locale', ['ru', 'en', 123, 3.14]);
            expect(block.serialize()).to.equal(r);
        });

        it('shouldn\'t quote null', function () {
            var r = 'ym:ge:locale==null';

            block = BEM.blocks[blockName].create('locale', null);
            expect(block.serialize()).to.equal(r);
        });
    });

    describe('Filter invert', function () {
        it('should invert OR serializer pattern', function () {
            block = BEM.blocks[blockName].create('city', [
                {op: '>', val: '1'},
                {op: '<', val: '2'},
            ], true);
            expect(block.serialize()).to.equal('NOT (ym:ge:regionCity>1 OR ym:ge:regionCity<2)');
        });

        it('should invert IN serializer pattern', function () {
            block = BEM.blocks[blockName].create('city', [
                {op: '==', val: '1'},
                {op: '==', val: '2'},
            ], true);
            expect(block.serialize()).to.equal('ym:ge:regionCity NOT IN (1,2)');
        });

        it('should invert special serializer pattern', function () {
            var r = 'NOT (exists ym:ge:device, ym:ge:specialDefaultDate with (ym:ge:eventType==\'EVENT_INIT\'))';

            block = BEM.blocks[blockName].create('newUsers', {op: '==', val: 1}, true);
            expect(block.serialize()).to.equal(r);
        });
    });

    describe('Filter special patterns', function () {
        it('newUsers should use special pattern', function () {
            var r = 'exists ym:ge:device, ym:ge:specialDefaultDate with (ym:ge:eventType==\'EVENT_INIT\')';

            block = BEM.blocks[blockName].create('newUsers', {op: '==', val: 1});
            expect(block.serialize()).to.equal(r);
        });

        it('organicInstalls should use special pattern', function () {
            var r = '(exists ym:ge:device, ym:ge:specialDefaultDate with (ym:ge:eventType==\'EVENT_INIT\') ' +
                'and none(ym:ge:eventType==\'EVENT_AD_INSTALL\'))';

            block = BEM.blocks[blockName].create('organicInstalls', {op: '==', val: 1});
            expect(block.serialize()).to.equal(r);
        });
    });
});
