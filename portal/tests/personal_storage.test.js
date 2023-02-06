const nock = require('nock');
const config = require('../../etc/config');
const ps = require('../libs/personal');

describe('personal_storage', function () {
    let req;
    const express_req_mock = {
        tvm: {
            datasync: {
                ticket: 'tvm_ticket'
            },
            user: {
                ticket: 'user_tvm_ticket'
            }
        }
    };

    beforeEach(function () {
        req = nock(config.ps.host);
    });
    after(function () {
        nock.restore();
    });
    describe('batch request', function () {
        const Batch_request = ps.Batch_request,
            items = [
                {
                    address_id: 'home',
                    address_line: 'somewhere',
                    longitude: 123.45,
                    latitude: 54.321
                },
                {
                    address_id: 'work',
                    address_line: 'elsewhere',
                    longitude: 67.890,
                    latitude: 98.76
                }
            ];

        this.timeout(1000);

        it('не ходит в сеть, если очередь пуста', function () {
            var batch = new Batch_request(express_req_mock, {
                uid: 12345
            });

            req.post('/v1/batch/request', '*').query(true).reply(200, 'bal');
            req.pendingMocks().should.not.be.empty;

            return batch.process().then(function (res) {
                res.length.should.be.empty;
                req.pendingMocks().should.not.be.empty;
            });
        });

        it('ходит в сеть с нужными параметрами и заголовками', function () {
            var batch = new Batch_request(express_req_mock, {
                    uid: 12345
                }),
                headers,
                query;

            batch.get_extracted_addresses();

            req
                .post('/v1/batch/request', function () {
                    return true;
                })
                .query(function (q) {
                    query = q;
                    return true;
                })
                .reply(function () {
                    headers = this.req.headers;
                    return [
                        200, JSON.stringify({
                            items: [
                                {
                                    code: 200,
                                    body: JSON.stringify({
                                        items: []
                                    })
                                }
                            ]
                        })
                    ];
                });

            return batch.process().then(function () {
                headers = Object.assign({}, headers);

                headers.should.have.property('x-ya-user-ticket')
                    .which.is.equal('user_tvm_ticket');
                headers.should.have.property('x-uid')
                    .which.is.equal(12345);
                headers.should.have.property('x-ya-service-ticket')
                    .which.is.equal('tvm_ticket');
                query.should.have.property('client_id').which.is.equal('portal-tune');
                query.should.have.property('client_name').which.is.equal('portal-tune');
            });
        });

        it('методы добавляются в очередь', function () {
            var batch = new Batch_request(express_req_mock, {
                    uid: 12345
                }),
                body;
            batch.get_extracted_addresses();
            batch.create_address(items[0]);
            batch.delete_address('work');

            req
                .post('/v1/batch/request', function () {
                    return true;
                })
                .query(true)
                .reply(200, function (uri, reqBody) {
                    body = JSON.parse(reqBody);
                    return JSON.stringify({
                        items: [
                            {
                                code: 200,
                                body: JSON.stringify({
                                    items: items.concat().reverse()
                                })
                            },
                            {
                                code: 201,
                                body: '{}'
                            },
                            {
                                code: 204,
                                body: '{}'
                            }
                        ]
                    });
                });

            return batch.process().then(function () {
                req.pendingMocks().should.be.empty;

                body.should.have.property('items')
                    .which.is.an('array');
                var request = body.items;
                request.should.have.lengthOf(3);
                request[0].should.deep.equal({
                    method: 'GET',
                    relative_url: '/v1/personality/profile/extracted_addresses'
                });

                request[1].should.deep.equal({
                    method: 'POST',
                    relative_url: '/v2/personality/profile/addresses',
                    body: JSON.stringify(items[0])
                });

                request[2].should.deep.equal({
                    method: 'DELETE',
                    relative_url: '/v2/personality/profile/addresses/work'
                });
            });
        });

        it('методы возвращают результат запроса', function () {
            var batch = new Batch_request(express_req_mock, {
                    uid: 12345
                }),
                promise = batch.get_extracted_addresses();

            req
                .post('/v1/batch/request', function () {
                    return true;
                })
                .query(true)
                .reply(200, function () {
                    return JSON.stringify({
                        items: [
                            {
                                code: 200,
                                body: JSON.stringify({
                                    items: items
                                })
                            }
                        ]
                    });
                });
            batch.process();

            return promise.then(function (result) {
                req.pendingMocks().should.be.empty;

                result.should.have.property('ok').which.is.equal(1);
                result.should.have.property('body')
                    .which.have.property('items').which.is.deep.equal(items);
            });
        });

        it('методы реджектятся при ошибки сети', function () {
            var batch = new Batch_request(express_req_mock, {
                    uid: 12345
                }),
                promise = batch.get_extracted_addresses();

            req
                .post('/v1/batch/request', function () {
                    return true;
                })
                .query(true)
                .reply(500);

            batch.process().catch(() => {
                /*
                 * Этот промис не зачем не нужен,
                 * но надо поймать ошибку, чтобы
                 * не было Unhandled rejection
                 */
            });

            return promise.then(function () {
                throw new Error('should fail');
            }, function (e) {
                req.pendingMocks().should.be.empty;
                e.should.have.property('statusCode')
                    .which.is.equal(500);
            });
        });

        it('методы получают ok:0 для "плохих" статусов', function () {
            var batch = new Batch_request(express_req_mock, {
                    uid: 12345
                }),
                promise = batch.get_extracted_addresses();

            req
                .post('/v1/batch/request', function () {
                    return true;
                })
                .query(true)
                .reply(200, function () {
                    return JSON.stringify({
                        items: [
                            {
                                code: 403,
                                body: JSON.stringify({
                                    message: 'Invalid upyachka'
                                })
                            }
                        ]
                    });
                });

            batch.process();

            return promise.then(function (result) {
                result.should.have.property('ok').which.is.equal(0);
                result.should.not.have.property('body');
                result.should.have.property('error')
                    .which.is.an('object')
                    .and.have.property('message').which.is.equal('Invalid upyachka');
            });
        });

        it('process возвращает результаты запросов', function () {
            var batch = new Batch_request(express_req_mock, {
                uid: 12345
            });

            batch.get_extracted_addresses();

            req
                .post('/v1/batch/request', function () {
                    return true;
                })
                .query(true)
                .reply(200, function () {
                    return JSON.stringify({
                        items: [
                            {
                                code: 200,
                                body: JSON.stringify({
                                    items: items
                                })
                            }
                        ]
                    });
                });

            return batch.process().then(function (result) {
                req.pendingMocks().should.be.empty;

                result.should.be.an('array');
                result.should.be.lengthOf(1);
                result[0].should.have.property('ok').which.is.equal(1);
                result[0].should.have.property('body')
                    .which.have.property('items').which.is.deep.equal(items);
            });
        });


        it('process реджектится при ошибки сети', function () {
            var batch = new Batch_request(express_req_mock, {
                uid: 12345
            });
            batch.get_extracted_addresses();

            req
                .post('/v1/batch/request', function () {
                    return true;
                })
                .query(true)
                .reply(500);

            return batch.process().then(function () {
                throw new Error('should fail');
            }, function (e) {
                req.pendingMocks().should.be.empty;
                e.should.have.property('statusCode')
                    .which.is.equal(500);
            });
        });

        it('process реджектится при отсутствии yandexuid\'а при записи по ui', function () {
            try {
                new Batch_request(express_req_mock, {
                    ui: 12345
                });
                throw new Error('constructor should throw');
            } catch (e) {
                e.message.should.equal('No yandexuid');
            }
        });

        describe('отправляются правильные заголовки', function () {
            let headers;

            beforeEach(() => {
                headers = null;
                nock.cleanAll();
                req
                    .post('/v1/batch/request', function () {
                        return true;
                    })
                    .query(true)
                    .reply(200, function () {
                        headers = this.req.headers;
                        return {
                            items: [
                                {
                                    body: '{}'
                                }
                            ]
                        };
                    });
            });

            it('паспортный uid', async function () {
                var batch = new Batch_request(express_req_mock, {
                    uid: 12345
                });
                batch.get_extracted_addresses();

                await batch.process();
                expect(headers).to.be.an('object');

                expect(headers).to.have.property('x-uid')
                    .which.equals(12345);
                expect(headers).to.have.property('x-ya-service-ticket')
                    .which.equals(express_req_mock.tvm.datasync.ticket);
                expect(headers).to.have.property('x-ya-user-ticket')
                    .which.equals(express_req_mock.tvm.user.ticket);
            });

            it('ui', async function () {
                var batch = new Batch_request(express_req_mock, {
                    yandexuid: 12345,
                    ui: 12345
                });
                batch.get_extracted_addresses();

                await batch.process();
                expect(headers).to.be.an('object');

                expect(headers).to.have.property('x-uid')
                    .which.equals('device-12345');
                expect(headers).to.have.property('x-ya-service-ticket')
                    .which.equals(express_req_mock.tvm.datasync.ticket);
                expect(headers).to.not.have.property('x-ya-user-ticket');
            });

            it('yandexuid', async function () {
                var batch = new Batch_request(express_req_mock, {
                    yandexuid: 12345
                });
                batch.get_extracted_addresses();

                await batch.process();
                expect(headers).to.be.an('object');

                expect(headers).to.have.property('x-uid')
                    .which.equals('yaid-12345');
                expect(headers).to.have.property('x-ya-service-ticket')
                    .which.equals(express_req_mock.tvm.datasync.ticket);
                expect(headers).to.not.have.property('x-ya-user-ticket');
            });
        });
    });

    describe('getPushes', function () {
        const reqMock = {
            tvm: {
                datasync: {
                    ticket: 'fakeTicket'
                }
            }
        };
        let headers = null;
        beforeEach(() => {
            headers = null;
            nock.cleanAll();
            req.get('/v1/personality/profile/yabrowser/configs_pushes')
                .reply(200, function () {
                    headers = this.req.headers;
                    return {
                        items: [
                            {
                                enabled: true,
                                topic: 'qwe',
                                uuid: 'qwe-uuid',
                                device_id: 'qwe-uuid',
                                schema_version: 1,
                                action_timestamp: new Date()
                            },
                            {
                                enabled: false,
                                topic: 'rty',
                                uuid: 'rty-uuid',
                                device_id: 'rty-uuid',
                                schema_version: 1,
                                action_timestamp: new Date()
                            }
                        ]
                    };
                });
        });
        it('реджектится без tvm тикета', function () {
            return ps.getPushes({}, {}).should.be.rejectedWith('has no TVM ticket for datasync');
        });

        it('реджектится без ui и yandexuid\'а', function () {
            return ps.getPushes(reqMock, {})
                .should.be.rejectedWith('No ui or yandexuid');
        });

        describe('x-uid', function () {
            it('валидный для ui', async function () {
                await ps.getPushes(reqMock, {ui: 'foo'});
                expect(headers).to.be.an('object')
                    .and.have.property('x-uid')
                    .which.equals('device-foo');

                expect(headers).to.have.property('x-ya-service-ticket')
                    .which.equals(reqMock.tvm.datasync.ticket);
                expect(headers).to.not.have.property('x-ya-user-ticket');
            });

            it('валидный для yandexuid\'а', async function () {
                await ps.getPushes(reqMock, {yandexuid: 1234567789});
                expect(headers).to.be.an('object')
                    .and.have.property('x-uid')
                    .which.equals('yaid-1234567789');

                expect(headers).to.have.property('x-ya-service-ticket')
                    .which.equals(reqMock.tvm.datasync.ticket);
                expect(headers).to.not.have.property('x-ya-user-ticket');
            });
        });

        it('формат ответа правильный', function () {
            return ps.getPushes(reqMock, {ui: 'foo'})
                .should.eventually.deep.equal({
                    qwe: true,
                    rty: false
                });
        });

        it('реджектится при плохом ответе датасинка', function () {
            nock.cleanAll();
            req.get('/v1/personality/profile/yabrowser/configs_pushes')
                .reply(401, function () {
                    return {
                    };
                });

            return expect(ps.getPushes(reqMock, {ui: 'foo'}))
                .to.be.rejectedWith('Unauthorized');
        });
    });

    describe('savePush', function () {
        const reqMock = {
            tvm: {
                datasync: {
                    ticket: 'fakeTicket'
                }
            },
            yandexuid: '1234567'
        };
        const mockPush = {
            topicId: 'qwe',
            enabled: true
        };
        let headers = null;
        let body = null;
        beforeEach(() => {
            headers = null;
            body = null;
            nock.cleanAll();
            req.put(/v1\/personality\/profile\/yabrowser\/configs_pushes/)
                .reply(200, function (uri, reqBody) {
                    headers = this.req.headers;
                    body = JSON.parse(reqBody);
                    return;
                });
        });
        afterEach(() => {
            nock.cleanAll();
        });
        after(() => {
            nock.restore();
        });
        it('реджектится без tvm тикета', function () {
            return ps.savePush({}, {})
                .should.be.rejectedWith('has no TVM ticket for datasync');
        });

        it('реджектится без ui и yandexuid\'а', function () {
            return ps.savePush(reqMock, mockPush)
                .should.be.rejectedWith('No ui or yandexuid');
        });

        describe('x-uid', function () {
            it('валидный для ui', async function () {
                await ps.savePush(reqMock, {ui: 'foo', yandexuid: 123456789, ...mockPush});
                expect(headers).to.be.an('object')
                    .and.have.property('x-uid')
                    .which.equals('device-foo');
            });

            it('валидный для yandexuid\'а', async function () {
                await ps.savePush(reqMock, {yandexuid: 1234567789, ...mockPush});
                expect(headers).to.be.an('object')
                    .and.have.property('x-uid')
                    .which.equals('yaid-1234567789');
            });
        });

        it('в запросе есть нужные заголовки', async function () {
            await ps.savePush(reqMock, {ui: 'foo', yandexuid: 123456789, ...mockPush});
            expect(headers).to.be.an('object');

            expect(headers).to.have.property('x-uid');
            expect(headers).to.have.property('x-ya-service-ticket')
                .which.equals(reqMock.tvm.datasync.ticket);
        });

        it('формат запроса правильный для ui', async function () {
            await ps.savePush(reqMock, {ui: 'foo', yandexuid: 123456789, ...mockPush});

            expect(body).be.an('object');

            expect({
                ...body,
                action_timestamp: null
            }).to.deep.equal({
                enabled: true,
                topic: 'qwe',
                uuid: 123456789,
                device_id: 'foo',
                schema_version: 1,
                action_timestamp: null
            });

            expect(new Date(body.action_timestamp) - new Date()).to.be.lessThan(1000);
        });

        it('формат запроса правильный для yandexuid\'а', async function () {
            await ps.savePush(reqMock, {yandexuid: 12345678788, ...mockPush});

            expect(body).be.an('object');

            expect({
                ...body,
                action_timestamp: null
            }).to.deep.equal({
                enabled: true,
                topic: 'qwe',
                uuid: 12345678788,
                device_id: 12345678788,
                schema_version: 1,
                action_timestamp: null
            });

            expect(new Date(body.action_timestamp) - new Date()).to.be.lessThan(1000);
        });

        it('реджектится без yandexuid\'а при сохранении по ui', function () {
            return expect(ps.savePush(reqMock, {ui: 'foo', ...mockPush}))
                .to.be.rejectedWith('No yandexuid');
        });

        it('реджектится при плохом ответе датасинка', function () {
            nock.cleanAll();
            req.put(/v1\/personality\/profile\/yabrowser\/configs_pushes/)
                .reply(401, function () {
                    return {
                    };
                });

            return expect(ps.savePush(reqMock, {ui: 'foo', yandexuid: 123456789}))
                .to.be.rejectedWith('Unauthorized');
        });
    });
});