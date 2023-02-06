describe('i-filters', function () {
    var expect = require('chai').expect,
        blockName = 'i-filters',
        block;

    beforeEach(function () {
        block = BEM.create(blockName);
    });

    afterEach(function () {
        if (block) {
            block.remove();
        }
    });

    describe('Filters singleton', function () {
        it('should be one instance', function () {
            expect(block.get()).to.deep.equal({});
            block.replace({city: [1]}, true);
            expect(block.get()).to.deep.equal({
                city: {
                    values: [{op: '==', val: '1'}],
                    inverted: false,
                },
            });

            expect(block.get()).to.deep.equal({
                city: {
                    values: [{op: '==', val: '1'}],
                    inverted: false,
                },
            });
        });
    });

    describe('Filters operations', function () {
        it('should replace all values', function () {
            block.add({city: ['1']});
            expect(block.get()).to.deep.equal({
                city: {
                    values: [{op: '==', val: '1'}],
                    inverted: false,
                },
            });

            block.replace({country: ['1']}, true);
            expect(block.get()).to.deep.equal({
                country: {
                    values: [{op: '==', val: '1'}],
                    inverted: false,
                },
            });
        });

        it('should replace one value', function () {
            block.add({city: [
                {op: '>', val: '1'},
                {op: '<', val: '2'},
            ]});
            expect(block.get()).to.deep.equal({
                city: {
                    values: [{op: '>', val: '1'}, {op: '<', val: '2'}],
                    inverted: false,
                },
            });

            block.replace({'city': ['1']});
            expect(block.get()).to.deep.equal({
                city: {
                    values: [{op: '==', val: '1'}],
                    inverted: false,
                },
            });
        });

        it('should add values', function () {
            block.add({city: ['>1']});
            expect(block.get()).to.deep.equal({
                city: {
                    values: [{op: '>', val: '1'}],
                    inverted: false,
                },
            });

            block.add({city: '<2'});
            expect(block.get()).to.deep.equal({
                city: {
                    values: [{op: '>', val: '1'}, {op: '<', val: '2'}],
                    inverted: false,
                },
            });
        });

        it('should remove values', function () {
            block.add({city: ['>1']});
            expect(block.get()).to.deep.equal({
                city: {
                    values: [{op: '>', val: '1'}],
                    inverted: false,
                },
            });

            block.remove('city');
            expect(block.get()).to.deep.equal({});
        });
    });

    describe('Filters serializer', function () {
        it('should serialize with AND', function () {
            var r = 'ym:ge:regionCity==1 AND ym:ge:regionCountry==2';

            block.add({'city': [1], 'country': [2]});

            expect(block.serialize()).to.equal(r);
        });

        it('should serialize with inverted filter', function () {
            var r = 'ym:ge:regionCity==1 AND NOT (ym:ge:regionCountry==2)';

            block.add({'city': [1], 'country': {inverted: true, values: [2]}});

            expect(block.serialize()).to.equal(r);
        });

        it('should use special hacks for campaign filter', function () {
            var r = '(exists ym:m:device with ((ym:m:eventType==\'EVENT_INIT\') AND ' +
                '(ym:m:specialDefaultDate>=\'2016-01-01\') AND (ym:m:specialDefaultDate<=\'2016-02-18\'))) AND ' +
                'exists ym:mc:device with (' +
                '(ym:mc:campaign==\'123456\') AND ' +
                '(ym:mc:specialDefaultDate>=\'2016-01-01\') AND ' +
                '(ym:mc:specialDefaultDate<=\'2016-02-18\'))';

            block.add({
                'cohortSegment': {
                    event: BEM.blocks['i-filter-cohort-segment'].EVENT_TYPE_INIT,
                    dates: {from: '2016-01-01', to: '2016-02-18'},
                },
                'campaign': '123456',
            });

            expect(block.serialize()).to.equal(r);
        });

        it('should serialize properly with some empty filters', function () {
            var r = 'ym:ge:gender==\'male\'';

            block.add({
                'cohortSegment': {
                    id: 'uniq106272880',
                    dates: {from: '2016-03-06', to: '2016-03-12'},
                },
                'gender': 'male',
            });
            expect(block.serialize()).to.equal(r);
        });

        it('should serialize into undefined with all empty filters', function () {
            block.add({
                'cohortSegment': [
                    {
                        id: 'uniq106272880',
                        dates: {from: '2016-03-06', to: '2016-03-12'},
                    },
                    {
                        id: 'uniq129600492',
                        dates: {from: '2016-03-08', to: '2016-03-14'},
                    },
                ],
            });
            expect(block.serialize()).to.equal(undefined);
        });

        it('should serialize conversion filter with quotes', function () {
            block.add({
                tConversion: {
                    op: '==',
                    'val': 'PHOTOSLICE_SYNC',
                },
            });
            expect(block.serialize()).to.equal('ym:ge:afterInstallEventName==\'PHOTOSLICE_SYNC\'');
        });
    });

    describe('Old segments processing', function () {
        it('should process old tree-filters values', function () {
            var oldFilters = {
                    'ym:mc:trackerParams': [
                        '["gender","m"]',
                        'age',
                    ],
                },
                newFilters = {
                    'trackerParams': [
                        ['gender', 'm'],
                        ['age'],
                    ],
                };

            expect(BEM.blocks['i-filters-old'].translateFiltersToNew(oldFilters)).to.deep.equal(newFilters);
        });
    });

});
