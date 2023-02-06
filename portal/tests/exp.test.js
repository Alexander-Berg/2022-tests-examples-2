const {makeInstance, Exp} = require('../exp');

describe('exp', function () {
    describe('isDisabled', function () {
        function create(disabled) {
            return makeInstance({
                id: 'test',
                till: ['2015-01-01'],
                disabled
            });
        }
        describe('должно быть false', function () {
            it('если нет disabled', function () {
                create().isDisabled().should.equal(false);
            });

            it('пустой массив', function () {
                create([]).isDisabled().should.equal(false);
            });

            it('ноль строкой', function () {
                create(['0']).isDisabled().should.equal(false);
            });

            it('пустая строка', function () {
                create(['']).isDisabled().should.equal(false);
            });

            it('если хотя бы один из disabled не true', function () {
                create([0, 4]).isDisabled().should.equal(false);
            });
        });

        describe('должно быть true', function () {
            it('если все disabled true', function () {
                create([1, 1]).isDisabled().should.equal(true);
            });
        });
    });

    describe('isExpired', function () {
        beforeEach(function () {
            sinon.useFakeTimers({now: new Date('2019-01-30')});
        });

        afterEach(function () {
            sinon.restore();
        });

        function create(till) {
            return makeInstance({
                id: 'test',
                till,
                disabled: [1]
            });
        }
        describe('должно быть false', function () {
            it('если нет till', function () {
                create().isExpired().should.equal(false);
            });

            it('пустой массив', function () {
                create([]).isExpired().should.equal(false);
            });

            it('без значения', function () {
                create(['']).isExpired().should.equal(false);
            });

            it('если хотя бы один из till моложе месяца', function () {
                create(['2019-01-01', '2019-01-03']).isExpired().should.equal(false);
            });
        });

        describe('должно быть true', function () {
            it('если все till старше месяца', function () {
                create(['2019-01-01', '2018-12-30']).isExpired().should.equal(true);
            });
        });
    });

    describe('isOff', function () {
        beforeEach(function () {
            sinon.useFakeTimers({now: new Date('2019-01-30')});
        });

        afterEach(function () {
            sinon.restore();
        });

        function create(percent, disabled, till) {
            return new Exp({
                id: 'test',
                percent,
                disabled,
                till: till || ['2019-01-01']
            });
        }
        describe('должно быть false', function () {
            it('если нет ничего', function () {
                create().isOff().should.equal(false);
            });

            it('если хотя бы один из percent - пустая строка', function () {
                create(['', 0]).isOff().should.equal(false);
            });

            it('если хотя бы один из percent не 0', function () {
                create([0, 4]).isOff().should.equal(false);
            });

            it('если хотя бы один из disabled не true', function () {
                create([0, 4], [0, 1]).isOff().should.equal(false);
            });

            it('если хотя бы один из till кончился', function () {
                create([0, 4], [0, 1], ['2019-01-01', '2019-01-03']).isOff().should.equal(false);
            });

            it('если нет процентов и есть till', function () {
                create(['', ''], ['', ''], ['2019-03-01', '']).isOff().should.equal(false);
            });

            it('если есть проценты и нет till', function () {
                create(['', '5'], ['', ''], ['', '']).isOff().should.equal(false);
            });
        });

        describe('должно быть true', function () {
            it('если все проценты 0 строкой', function () {
                create(['0', '0']).isOff().should.equal(true);
            });

            it('если все проценты 0', function () {
                create([0, 0]).isOff().should.equal(true);
            });

            it('если стоит disabled', function () {
                create([0, 4], [1, 1]).isOff().should.equal(true);
            });

            it('если нет процентов и till', function () {
                create(['', ''], ['', ''], ['', '']).isOff().should.equal(true);
            });

            it('если проценты = 0 и нет till', function () {
                create(['', '0'], ['', ''], ['', '']).isOff().should.equal(true);
            });
        });
    });

    describe('isOn', function () {
        function create(percent, disabled) {
            return makeInstance({
                id: 'test',
                percent,
                disabled,
                till: ['2019-01-01']
            });
        }
        describe('должно быть false', function () {
            it('если isOff', function () {
                create([0, 0]).isOn().should.equal(false, 'все нули');
                create(['']).isOn().should.equal(false, 'пустая строка');
                create(['0']).isOn().should.equal(false, 'ноль строкой');
                create([0, 4], [1, 1]).isOn().should.equal(false, 'disabled');
            });
        });

        describe('должно быть true', function () {
            it('если все проценты 100 строкой', function () {
                create(['100', '100'], [0, 1]).isOn().should.equal(true);
            });

            it('если все проценты 100', function () {
                create([100, 100], [0, 1]).isOn().should.equal(true);
            });
        });
    });

    describe('isInternal', function () {
        function create(yandex = false, yandex_669 = false, yandex_disabled = false) {
            return makeInstance({
                id: 'test',
                disabled: [1],
                yandex,
                yandex_669,
                yandex_disabled
            });
        }
        describe('должно быть false', function () {
            it('если все флаги false', function () {
                create().isInternal().should.equal(false);
            });

            it('если yandex_disabled', function () {
                create(true, true, true).isInternal().should.equal(false);
            });
        });

        describe('должно быть true', function () {
            it('yandex', function () {
                expect(create(true, false)).to.be.undefined;
            });
            it('yandex_669', function () {
                expect(create(false, true)).to.be.undefined;
            });
        });
    });
});