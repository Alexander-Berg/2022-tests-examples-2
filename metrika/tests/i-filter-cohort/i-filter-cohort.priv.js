describe('i-filter-cohort', function () {
    var expect = require('chai').expect,
        blockName = 'i-filter-cohort',
        block;

    afterEach(function () {
        if (block) {
            block.destruct();
        }
    });

    describe('Filter constructor', function () {
        it('should accept empty value', function () {
            block = BEM.blocks[blockName].create('cohort', []);
            expect(block.get().values).to.deep.equal([]);
        });

        it('should accept single simple value', function () {
            var r = {
                val: undefined,
                dates: ['2016-01-01', '2016-02-18'],
            };

            block = BEM.blocks[blockName].create('cohort', {dates: '2016-01-01, 2016-02-18'});
            expect(block.get().values).to.deep.equal([r]);
        });

        it('should accept single value with all fields', function () {
            var r = {
                val: 'aa',
                dates: ['2016-01-01', '2016-02-18'],
            };

            block = BEM.blocks[blockName].create('cohort', r);
            expect(block.get().values).to.deep.equal([r]);
        });

        it('should accept campaign or publisher in op,val object', function () {
            var r = {
                val: '123456',
                dates: [BEM.blocks[blockName].DEFAULT_START_DATE, BEM.blocks[blockName].getCurrentDate()],
            };

            block = BEM.blocks[blockName].create('campaign', {op: '==', val: '123456'});
            expect(block.get().values).to.deep.equal([r]);
        });
    });

    describe('Filter operations', function () {
        it('should replace values', function () {
            var r = {
                val: undefined,
                dates: ['2016-02-01', '2016-02-18'],
            };

            block = BEM.blocks[blockName].create('cohort', {dates: ['2016-01-01', '2016-02-18']});

            block.replace({dates: ['2016-02-01', '2016-02-18']});

            expect(block.get().values).to.deep.equal([r]);
        });

        it('should add values', function () {
            var r = [
                {
                    val: undefined,
                    dates: ['2016-01-01', '2016-02-18'],
                },
                {
                    val: undefined,
                    dates: ['2016-02-01', '2016-02-18'],
                },
            ];

            block = BEM.blocks[blockName].create('cohort', {dates: ['2016-01-01', '2016-02-18']});

            block.add({dates: ['2016-02-01', '2016-02-18']});

            expect(block.get().values).to.deep.equal(r);
        });

        it('should remove values', function () {
            var r = {
                val: undefined,
                dates: ['2016-01-01', '2016-02-18'],
            };

            block = BEM.blocks[blockName].create('cohort', [
                {dates: ['2016-01-01', '2016-02-18']},
                {dates: ['2016-02-01', '2016-02-18']},
            ]);

            block.remove({dates: ['2016-02-01', '2016-02-18']});

            expect(block.get().values).to.deep.equal([r]);
        });
    });

    describe('Filter serializer', function () {
        it('should serialize simple value', function () {
            var r = 'exists ym:m:device with ((ym:m:eventType==\'EVENT_INIT\') AND ' +
                '(ym:m:specialDefaultDate>=\'2016-01-01\') AND (ym:m:specialDefaultDate<=\'2016-02-18\'))';

            block = BEM.blocks[blockName].create('cohort', {dates: ['2016-01-01', '2016-02-18']});
            expect(block.serialize()).to.equal(r);
        });

        it('should serialize full value', function () {
            var r = 'exists ym:m:device with ((ym:m:eventType==\'EVENT_INIT\') AND ' +
                '(ym:m:eventLabel==\'aaa\')' +
                ' AND (ym:m:specialDefaultDate>=\'2016-01-01\') AND (ym:m:specialDefaultDate<=\'2016-02-18\'))';

            block = BEM.blocks[blockName].create('cohort', {
                val: 'aaa',
                dates: ['2016-01-01', '2016-02-18'],
            });
            expect(block.serialize()).to.equal(r);
        });

        it('should serialize multiple values', function () {
            var r = '(exists ym:m:device with ((ym:m:eventType==\'EVENT_INIT\') AND ' +
                '(ym:m:eventLabel==\'aaa\')' +
                ' AND (ym:m:specialDefaultDate>=\'2016-01-01\') AND (ym:m:specialDefaultDate<=\'2016-02-18\'))' +
                ' OR exists ym:m:device with ((ym:m:eventType==\'EVENT_INIT\') AND ' +
                '(ym:m:eventLabel==\'bbb\')' +
                ' AND (ym:m:specialDefaultDate>=\'2016-02-01\') AND (ym:m:specialDefaultDate<=\'2016-02-07\')))';

            block = BEM.blocks[blockName].create('cohort', [
                {
                    val: 'aaa',
                    dates: ['2016-01-01', '2016-02-18'],
                },
                {
                    val: 'bbb',
                    dates: ['2016-02-01', '2016-02-07'],
                },
            ]);

            expect(block.serialize()).to.equal(r);
        });

        it('campaign should use special pattern', function () {
            var r = 'exists ym:mc:device with (' +
                    '(ym:mc:campaign==\'123456\') AND ' +
                    '(ym:mc:specialDefaultDate>=\'' + BEM.blocks[blockName].DEFAULT_START_DATE + '\') AND ' +
                    '(ym:mc:specialDefaultDate<=\'' + BEM.blocks[blockName].getCurrentDate() + '\'))';

            block = BEM.blocks[blockName].create('campaign', '123456');
            expect(block.serialize()).to.equal(r);
        });

        it('publisher should use special pattern', function () {
            var r = 'exists ym:mc:device with (' +
                '(ym:mc:publisher==\'123456\') AND ' +
                '(ym:mc:specialDefaultDate>=\'' + BEM.blocks[blockName].DEFAULT_START_DATE + '\') AND ' +
                '(ym:mc:specialDefaultDate<=\'' + BEM.blocks[blockName].getCurrentDate() + '\'))';

            block = BEM.blocks[blockName].create('publisher', '123456');
            expect(block.serialize()).to.equal(r);
        });

        it('campaign should support inverted state', function () {
            var r = 'NOT exists ym:mc:device with (' +
                '(ym:mc:campaign==\'123456\') AND ' +
                '(ym:mc:specialDefaultDate>=\'' + BEM.blocks[blockName].DEFAULT_START_DATE + '\') AND ' +
                '(ym:mc:specialDefaultDate<=\'' + BEM.blocks[blockName].getCurrentDate() + '\'))';

            block = BEM.blocks[blockName].create('campaign', '123456');
            expect(block.setInverted(true).serialize()).to.equal(r);
        });
    });

});
