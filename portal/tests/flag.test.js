const {makeInstance} = require('../flag');

describe('flag', function () {
    const DAY = 24 * 60 * 60 * 1000,
        FOUR_WEEKS = 4 * 7 * DAY,
        MINUTE = 60 * 1000;
    describe('isFirstPing', function () {
        /*
        let sandbox;
        beforeEach(function () {
            sandbox = sinon.createSandbox({
                useFakeTimers: true
            });
        });
        afterEach(function () {
            sandbox.restore();
        });*/
        let expireDate;
        function create(expire) {
            return makeInstance({
                id: 'test',
                expire,
                percent: [100]
            });
        }
        function assertTimeDeltas(value, deltas) {
            describe(`должно быть ${value}`, function () {
                deltas.forEach(delta => {
                    it(`${delta} дней`, function () {
                        const date = new Date(+expireDate + delta * DAY);
                        sinon.useFakeTimers({now: +date});
                        create(expireDate).isFirstPing().should.equal(value, date.toLocaleDateString('ru'));
                    });
                });
            });
        }
        afterEach(function () {
            sinon.restore();
        });
        describe('expire минус 4 недели - пятница', function () {
            beforeEach(function () {
                expireDate = new Date(new Date(2019, 6, 5) + FOUR_WEEKS + MINUTE);
            });
            const deltas = [];
            for (let i = -30; i < 30; i++) {
                if (i !== -28) {
                    deltas.push(i);
                }
            }
            assertTimeDeltas(false, deltas);
            assertTimeDeltas(true, [-28]);
        });

        describe('expire минус 4 недели - суббота', function () {
            beforeEach(function () {
                expireDate = new Date(new Date(2019, 6, 6) + FOUR_WEEKS + MINUTE);
            });
            const deltas = [];
            for (let i = -30; i < 30; i++) {
                if (i !== -26) {
                    deltas.push(i);
                }
            }
            assertTimeDeltas(false, deltas);
            assertTimeDeltas(true, [-26]);
        });

        describe('expire минус 4 недели - воскресенье', function () {
            beforeEach(function () {
                expireDate = new Date(new Date(2019, 6, 7) + FOUR_WEEKS + MINUTE);
            });
            const deltas = [];
            for (let i = -30; i < 30; i++) {
                if (i !== -27) {
                    deltas.push(i);
                }
            }
            assertTimeDeltas(false, deltas);
            assertTimeDeltas(true, [-27]);
        });
    });

    describe('isOff', function () {
        function create(percent, disabled) {
            return makeInstance({
                id: 'test',
                expire: -1,
                percent,
                disabled
            });
        }
        describe('должно быть false', function () {
            it('если нет процентов', function () {
                create().isOff().should.equal(false);
            });

            it('если хотя бы один из percent не 0', function () {
                create([0, 4]).isOff().should.equal(false);
            });

            it('если хотя бы один из disabled не true', function () {
                create([0, 4], [0, 1]).isOff().should.equal(false);
            });
        });

        describe('должно быть true', function () {
            it('если все проценты 0', function () {
                create([0, 0]).isOff().should.equal(true);
            });

            it('если стоит disabled', function () {
                create([0, 4], [1, 1]).isOff().should.equal(true);
            });
        });
    });

    describe('isOn', function () {
        function create(percent, disabled, yandex_only = [1]) {
            return makeInstance({
                id: 'test',
                expire: -1,
                percent,
                disabled,
                yandex_only
            });
        }
        describe('должно быть false', function () {
            it('если isOff', function () {
                create([0, 0]).isOn().should.equal(false, 'все нули');
                create([0, 4], [1, 1]).isOn().should.equal(false, 'disabled');
            });

            it('yandex_only', function () {
                create([100, 100], [0, 1], [1]).isOn().should.equal(false);
            });
        });

        describe('должно быть true', function () {
            it('если все проценты 100', function () {
                create([100, 100], [0, 1], [0]).isOn().should.equal(true);
            });
        });
    });

    describe('isExpireSoon', function () {
        function create(expire) {
            return makeInstance({
                id: 'test',
                expire,
                percent: [100]
            });
        }
        const now = Date.now();

        it('должно быть true', function () {
            for (let i = -7; i < 14; i++) {
                create(new Date(now + i * DAY)).isExpireSoon().should.equal(true, `${i} дней`);
            }
        });

        it('должно быть false', function () {
            for (let i = 15; i < 30; i++) {
                create(new Date(now + i * DAY)).isExpireSoon().should.equal(false, `${i} дней`);
            }
        });
    });

    describe('isInternal', function () {
        function create(yandex100, yandex_only) {
            return makeInstance({
                id: 'test',
                expire: -1,
                yandex100,
                yandex_only
            });
        }
        describe('должно быть false', function () {
            it('если пустые массивы', function () {
                create([], []).isInternal().should.equal(false);
            });

            it('если не yandex100 и yandex_only', function () {
                create([0, 0], [0, 0]).isInternal().should.equal(false, 'все нули');
                create([0, 1], [0, 1]).isInternal().should.equal(false, 'не все нули');
            });
        });

        describe('должно быть true', function () {
            it('все yandex_only = 1', function () {
                create([0, 0], [1, 1]).isInternal().should.equal(true);
            });
            it('все yandex100 = 1', function () {
                create([1, 1], [0, 0]).isInternal().should.equal(true);
            });
        });
    });


    describe('formatExportStatus', function () {
        function create({
            percent = [],
            till = [],
            yandex100 = [],
            yandex_only = [],
            disabled = []
        } = {}) {
            return makeInstance({
                id: 'test',
                expire: -1,
                inExport: true,
                desc: [],
                disabled,
                till,
                percent,
                yandex100,
                yandex_only
            });
        }
        it('возвращает пустоту, если не inExport', function () {
            makeInstance({id: 'test', expire: -1}).formatExportStatus().should.equal('');
        });

        it('выключен', function () {
            const status = create({disabled: [1]}).formatExportStatus();
            status.should.have.string('| disabled |')
                .and.have.string('| 1 |')
                .and.not.have.string('undefined');

        });

        it('включен на 0', function () {
            const status = create({percent: [0, 0]}).formatExportStatus();
            status.should.have.string('| percent |')
                .and.have.string('| 0 |')
                .and.not.have.string('undefined');

        });

        it('завершен в прошлом', function () {
            const status = create({till: ['2015-08-04', '2019-01-01']}).formatExportStatus();

            status.should.have.string('| till |')
                .and.have.string('| 2015-08-04 |')
                .and.have.string('| 2015-08-04 |')
                .and.not.have.string('undefined');


        });

        it('общий случай', function () {
            let status = create({disabled: [1, 0]}).formatExportStatus();
            status.should.have.string('| disabled |')
                .and.have.string('| 1 |')
                .and.have.string('| 0 |')
                .and.not.have.string('undefined');

            status = create({percent: [0, 50, 100]}).formatExportStatus();
            status.should.have.string('| percent |')
                .and.have.string('| 0 |')
                .and.have.string('| 50 |')
                .and.have.string('| 100 |')
                .and.not.have.string('undefined');

            status = create({till: ['2015-08-04', '20000-08-04']}).formatExportStatus();
            status.should.have.string('| till |')
                .and.have.string('| 2015-08-04 |')
                .and.have.string('| 20000-08-04 |')
                .and.not.have.string('undefined');
        });

        describe('внутренняя сеть', function () {
            it('отображается для yandex_only', function () {
                const status = create({yandex_only: [1, 1], percent: [10, 50]}).formatExportStatus();
                status.should.have.string('| yandex_only |')
                    .and.have.string('| 1 |')
                    .and.have.string('| percent |')
                    .and.have.string('| 10 |')
                    .and.have.string('| 50 |')
                    .and.not.have.string('undefined');
            });

            it('отображается для yandex100', function () {
                const status = create({yandex100: [1, 1]}).formatExportStatus();
                status.should.have.string('| yandex100 |')
                    .and.have.string('| 1 |')
                    .and.not.have.string('undefined');
            });
        });
    });

    describe('formatComment', function () {
        function create(expire, {files = [], inExport = false} = {}) {
            return makeInstance({
                id: 'test',
                expire: new Date(expire),
                files,
                inExport,
                disabled: [],
                desc: [],
                filter: [],
                content: [],
                geos: [],
                domain: [],
                till: [],
                percent: [],
                yandex100: [1]
            });
        }
        const openTask = {
                status: {
                    key: 'open'
                },
                components: [
                    {key: '#Code'}
                ]
            },
            taskInProgress = {
                status: {
                    key: 'in_progress'
                },
                components: [
                    {key: '#UI'}
                ]
            };

        describe('Разные даты', function () {
            it('сегодня', function () {
                create(Date.now()).formatComment(openTask).should.have.string('Флаг истекает сегодня');
            });

            it('в прошлом', function () {
                for (let i = 1; i < 10; i++) {
                    create(Date.now() - i * DAY).formatComment(openTask).should.have.string(`Флаг истёк ${i} дней назад`);
                }
            });

            it('в будущем', function () {
                for (let i = 1; i < 10; i++) {
                    create(Date.now() + i * DAY).formatComment(openTask).should.have.string(`Флаг истекает через ${i} дней`);
                }
            });
        });

        describe('просьба', function () {
            it('присутствует для тасков в статусе "Открыт"', function () {
                create(Date.now()).formatComment(openTask).should.have.string('напишите результат');
            });

            it('отсутствует для других статусов', function () {
                create(Date.now()).formatComment(taskInProgress).should.not.have.string('возьмите этот таск в работу');
            });
        });

        describe('изменения в компонентах', function () {
            describe('вычистка ui', function () {
                it('добавляет информацию в #UI таск', function () {
                    create(Date.now(), {files: ['lib/bla']}).formatComment(taskInProgress).should.have.string('lib/bla');
                });

                it('не добавляет информацию в #Code таск', function () {
                    create(Date.now(), {files: ['lib/bla']}).formatComment(openTask).should.not.have.string('lib/bla');
                });
            });
            describe('вычистка code', function () {
                it('добавляет информацию в #Code таск', function () {
                    create(Date.now(), {files: ['tmpl/bla']}).formatComment(openTask).should.have.string('tmpl/bla');
                });

                it('не добавляет информацию в #Ui таск', function () {
                    create(Date.now(), {files: ['tmpl/bla']}).formatComment(taskInProgress).should.not.have.string('tmpl/bla');
                });
            });
        });
        describe('кат', function () {
            it('не используется при небольшом количестве строк', function () {
                create(Date.now(), {files: []}).formatComment(openTask).should.not.have.string('<{');
            });
            it('используется при большом количестве строк', function () {
                create(Date.now(), {files: [], inExport: true}).formatComment(openTask).should.have.string('<{');
            });
        });
    });
});