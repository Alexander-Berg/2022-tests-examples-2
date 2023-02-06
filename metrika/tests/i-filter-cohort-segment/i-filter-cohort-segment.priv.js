describe('i-filter-cohort-segment', function () {
    var expect = require('chai').expect,
        blockName = 'i-filter-cohort-segment',
        block;

    afterEach(function () {
        if (block) {
            block.destruct();
        }
    });

    describe('Filter constructor', function () {
        it('should accept empty value', function () {
            block = BEM.blocks[blockName].create('cohortSegment', []);
            expect(block.get().values).to.deep.equal([]);
        });

        it('should accept undefined event value', function () {
            var r = {
                dates: {from: '2016-01-01', to: '2016-02-18'},
                inverted: false,
            };

            block = BEM.blocks[blockName].create('cohortSegment', {
                event: undefined,
                dates: {from: '2016-01-01', to: '2016-02-18'},
            });
            expect(block.get().values).to.deep.equal([r]);
        });

        it('should accept single simple value', function () {
            var r = {
                event: BEM.blocks[blockName].EVENT_TYPE_INIT,
                dates: {from: '2016-01-01', to: '2016-02-18'},
                inverted: false,
            };

            block = BEM.blocks[blockName].create('cohortSegment', {
                event: BEM.blocks[blockName].EVENT_TYPE_INIT,
                dates: {from: '2016-01-01', to: '2016-02-18'},
            });
            expect(block.get().values).to.deep.equal([r]);
        });

        it('should accept single value with all fields', function () {
            var r = {
                event: BEM.blocks[blockName].EVENT_TYPE_INIT,
                dates: {from: '2016-01-01', to: '2016-02-18'},
                eventsNum: [1, 10],
                inverted: true,
            };

            block = BEM.blocks[blockName].create('cohortSegment', r);
            expect(block.get().values).to.deep.equal([{
                event: BEM.blocks[blockName].EVENT_TYPE_INIT,
                dates: {from: '2016-01-01', to: '2016-02-18'},
                eventsNum: {
                    op: BEM.blocks[blockName].BETWEEN_OP,
                    val: [1, 10],
                },
                inverted: true,
            }]);
        });
    });

    describe('Filter operations', function () {
        it('should replace values', function () {
            var r = {
                event: 'ololo',
                dates: {from: '2016-01-01', to: '2016-01-18'},
                inverted: true,
            };

            block = BEM.blocks[blockName].create('cohortSegment', {
                event: BEM.blocks[blockName].EVENT_TYPE_INIT,
                dates: {from: '2016-01-01', to: '2016-02-18'},
            });

            block.replace({
                event: 'ololo',
                dates: {from: '2016-01-01', to: '2016-01-18'},
                inverted: true,
            });

            expect(block.get().values).to.deep.equal([r]);
        });

        it('should add values', function () {
            var r = [
                {
                    event: BEM.blocks[blockName].EVENT_TYPE_INIT,
                    dates: {from: '2016-01-01', to: '2016-02-18'},
                    inverted: false,
                },
                {
                    event: 'ololo',
                    dates: {from: '2016-01-01', to: '2016-01-18'},
                    inverted: true,
                },
            ];

            block = BEM.blocks[blockName].create('cohortSegment', {
                event: BEM.blocks[blockName].EVENT_TYPE_INIT,
                dates: {from: '2016-01-01', to: '2016-02-18'},
            });

            block.add({
                event: 'ololo',
                dates: {from: '2016-01-01', to: '2016-01-18'},
                inverted: true,
            });

            expect(block.get().values).to.deep.equal(r);
        });

        it('should remove values', function () {
            var r = {
                event: 'ololo',
                dates: {from: '2016-01-01', to: '2016-01-18'},
                inverted: true,
            };

            block = BEM.blocks[blockName].create('cohortSegment', [
                {
                    event: BEM.blocks[blockName].EVENT_TYPE_INIT,
                    dates: {from: '2016-01-01', to: '2016-02-18'},
                    eventsNum: undefined,
                    inverted: false,
                },
                {
                    event: 'ololo',
                    dates: {from: '2016-01-01', to: '2016-01-18'},
                    eventsNum: undefined,
                    inverted: true,
                },
            ]);

            block.remove({
                event: BEM.blocks[blockName].EVENT_TYPE_INIT,
                dates: {from: '2016-01-01', to: '2016-02-18'},
            });

            expect(block.get().values).to.deep.equal([r]);
        });
    });

    describe('Filter serializer', function () {
        it('should NOT serialize simple value with undefined event', function () {
            var r = '';

            block = BEM.blocks[blockName].create('cohortSegment', {
                event: undefined,
                dates: {from: '2015-10-15', to: '2015-12-07'},
            });
            expect(block.serialize()).to.equal(r);
        });

        it('should serialize simple value with internal event', function () {
            var r = '(exists ym:m:device with ((ym:m:eventType==\'EVENT_INIT\') AND ' +
                '(ym:m:specialDefaultDate>=\'2015-10-15\') AND (ym:m:specialDefaultDate<=\'2015-12-07\')))';

            block = BEM.blocks[blockName].create('cohortSegment', {
                event: BEM.blocks[blockName].EVENT_TYPE_INIT,
                dates: {from: '2015-10-15', to: '2015-12-07'},
            });
            expect(block.serialize()).to.equal(r);
        });

        it('should serialize simple value with user event', function () {
            var r = '(exists ym:m:device with ((ym:m:eventFlat==\'CALL_PHONE\') AND ' +
                '(ym:m:specialDefaultDate>=\'2015-10-15\') AND (ym:m:specialDefaultDate<=\'2015-12-07\')))';

            block = BEM.blocks[blockName].create('cohortSegment', {
                event: 'CALL_PHONE',
                dates: {from: '2015-10-15', to: '2015-12-07'},
            });
            expect(block.serialize()).to.equal(r);
        });

        it('should serialize inverted value', function () {
            var r = '(NOT (exists ym:m:device with ((ym:m:eventFlat==\'OPEN_CARD_FAVORITE\') AND ' +
                '(ym:m:specialDefaultDate>=\'2015-11-27\') AND (ym:m:specialDefaultDate<=\'2015-12-03\'))))';

            block = BEM.blocks[blockName].create('cohortSegment', {
                event: 'OPEN_CARD_FAVORITE',
                dates: {from: '2015-11-27', to: '2015-12-03'},
                inverted: true,
            });
            expect(block.serialize()).to.equal(r);
        });

        it('should serialize values with events number', function () {
            var r = '(exists ym:m:device with ((ym:m:eventFlat==\'SEARCH HOMES\') AND ' +
                '(ym:m:specialDefaultDate>=\'2014-12-15\') AND (ym:m:clientEvents>=10) AND ' +
                '(ym:m:clientEvents<=42)))';

            block = BEM.blocks[blockName].create('cohortSegment', {
                event: 'SEARCH HOMES',
                dates: {from: '2014-12-15'},
                eventsNum: {op: '><', val: [10, 42]},
            });

            expect(block.serialize()).to.equal(r);
        });

        it('should serialize values with empty events number', function () {
            var r = '(exists ym:m:device with ((ym:m:eventFlat==\'SEARCH HOMES\') AND ' +
                '(ym:m:specialDefaultDate>=\'2014-12-15\')))';

            block = BEM.blocks[blockName].create('cohortSegment', {
                event: 'SEARCH HOMES',
                dates: {from: '2014-12-15'},
                eventsNum: {op: '><', val: ['', '']},
            });

            expect(block.serialize()).to.equal(r);
        });

        it('should serialize tree values', function () {
            var r = '(exists ym:m:device with (exists ym:m:device with (ym:m:paramsLevel1==\'event1\') AND ' +
                'ym:m:eventLabel==\'SEARCH HOMES\' AND ' +
                '(ym:m:specialDefaultDate>=\'2014-12-15\') AND ' +
                '(ym:m:clientEvents>10)))';

            block = BEM.blocks[blockName].create('cohortSegment', {
                event: {tree: ['SEARCH HOMES', 'event1']},
                dates: {from: '2014-12-15'},
                eventsNum: {op: '>', val: 10},
            });

            expect(block.serialize()).to.equal(r);
        });

        it('should serialize multiple values', function () {
            var r = '((exists ym:m:device with ((ym:m:eventType==\'EVENT_INIT\') AND ' +
                '(ym:m:specialDefaultDate>=\'2016-01-01\') AND (ym:m:specialDefaultDate<=\'2016-02-18\'))) AND ' +
                '(NOT (exists ym:m:device with ((ym:m:eventFlat==\'ololo\') AND ' +
                '(ym:m:specialDefaultDate>=\'2016-01-01\') AND (ym:m:specialDefaultDate<=\'2016-01-18\')))))';

            block = BEM.blocks[blockName].create('cohortSegment', [
                {
                    event: BEM.blocks[blockName].EVENT_TYPE_INIT,
                    dates: {from: '2016-01-01', to: '2016-02-18'},
                },
                {
                    event: 'ololo',
                    dates: {from: '2016-01-01', to: '2016-01-18'},
                    inverted: true,
                },
            ]);
            expect(block.serialize()).to.equal(r);
        });

        it('should serialize complex cohort value', function () {
            var r = '(exists ym:m:device with (exists ym:m:device with (ym:m:paramsValueDouble==34) AND ' +
                'ym:m:eventLabel==\'url opened\' AND ' +
                '(ym:m:specialDefaultDate>=\'2016-03-17\') AND (ym:m:specialDefaultDate<=\'2016-03-23\')))';

            block = BEM.blocks[blockName].create('cohortSegment', {
                'id': 'uniq113861702',
                'event': [
                    {
                        'tree': [
                            'url opened',
                        ],
                        'op': '==',
                        'val': '34',
                    },
                ],
                'dates': {
                    'from': '2016-03-17',
                    'to': '2016-03-23',
                },
                'eventsNum': {
                    'op': '==',
                    'val': '',
                },
                'inverted': false,
            });
            expect(block.serialize()).to.equal(r);
        });

    });

    describe('isEmpty', function () {
        it('should return true for cohorts without event', function () {
            var block = BEM.blocks[blockName].create('cohortSegment', [
                {
                    dates: {from: '2016-01-01', to: '2016-02-18'},
                    inverted: false,
                },
                {
                    dates: {from: '2016-01-01', to: '2016-01-18'},
                    inverted: true,
                },
            ]);

            expect(block.isEmpty()).to.equal(true);
        });

        it('should return false for cohorts with event', function () {
            var block = BEM.blocks[blockName].create('cohortSegment', [
                {
                    event: [{tree: ['0', '1']}],
                    dates: {from: '2016-01-01', to: '2016-02-18'},
                    inverted: false,
                },
                {
                    dates: {from: '2016-01-01', to: '2016-01-18'},
                    inverted: true,
                },
            ]);

            expect(block.isEmpty()).to.equal(false);
        });
    });
});
