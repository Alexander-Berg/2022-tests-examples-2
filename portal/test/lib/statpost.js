'use strict';

const _ = require('lodash');
const q = require('q');
const qs = require('qs');
const Statpost = require('../../lib/statpost');
const qhttp = require('q-io/http');

describe('Statpost', () => {
    const sandbox = sinon.sandbox.create();

    beforeEach(() => {
        sandbox.stub(qhttp, 'read')
            .named('qhttp.read')
            .returns(q('{}'));
    });

    afterEach(() => {
        sandbox.restore();
    });

    describe('reportData', () => {
        it('should post data to statface', () => {
            const dataToSend = {
                dataName: 'some_data',
                data: {key: 'value'}
            };

            const expected = qs.stringify({
                scale: 'i',
                name: 'some_data',
                json_data: JSON.stringify({values: {key: 'value'}})
            });

            return doPost_(dataToSend)
                .then(() => {
                    expect(qhttp.read).to.be.calledWithMatch({body: [expected]});
                });
        });

        it('should post data to stat-beta.yandex-team.ru if beta instance set', () => {
            return doPost_({betaInstance: true})
                .then(() => {
                    expect(qhttp.read)
                        .to.be.calledWithMatch({url: 'https://stat-beta.yandex-team.ru/_api/report/data'});
                });
        });

        it('should post data to stat.yandex-team.ru by default', () => {
            return doPost_()
                .then(() => {
                    expect(qhttp.read)
                        .to.be.calledWithMatch({url: 'https://stat.yandex-team.ru/_api/report/data'});
                });
        });

        it('should post data with specific scale if it passed', () => {
            const dataToSend = {
                scale: 'scale',
                dataName: 'some_data',
                data: {key: 'value'}
            };

            const expected = qs.stringify({
                scale: 'scale',
                name: 'some_data',
                json_data: JSON.stringify({values: {key: 'value'}})
            });

            return doPost_(dataToSend)
                .then(() => {
                    expect(qhttp.read).to.be.calledWithMatch({body: [expected]});
                });
        });

        it('should post data with min scale by default', () => {
            const dataToSend = {
                dataName: 'some_data',
                data: {key: 'value'}
            };

            const expected = qs.stringify({
                scale: 'i',
                name: 'some_data',
                json_data: JSON.stringify({values: {key: 'value'}})
            });

            return doPost_(dataToSend)
                .then(() => {
                    expect(qhttp.read).to.be.calledWithMatch({body: [expected]});
                });
        });

        it('should add robot`s username and password to request headers if they set', () => {
            return doPost_({username: 'robot', password: 'robopass'})
                .then(() => {
                    expect(qhttp.read).to.be.calledWithMatch({
                        headers: {
                            StatRobotUser: 'robot',
                            StatRobotPassword: 'robopass'
                        }
                    });
                });
        });

        it('should resolve with statface response', () => {
            qhttp.read.returns(q('{"status": "OK"}'));

            return expect(doPost_()).to.be.eventually.become({status: 'OK'});
        });

        it('should reject if failed to post data', () => {
            qhttp.read.returns(q.reject(new Error('something went wrong')));

            return expect(doPost_()).to.be.rejectedWith('something went wrong');
        });

        it('should read err info from error response body if possible', () => {
            const err = {
                response: {
                    body: {
                        read: sandbox.stub().returns(q('err response body'))
                    }
                }
            };
            qhttp.read.returns(q.reject(err));

            return expect(doPost_()).to.be.rejectedWith('err response body');
        });
    });

    function doPost_(params) {
        params = _.defaults(params || {}, {
            betaInstance: false,
            username: 'default_user',
            password: 'default_password',
            dataName: 'default_data_name',
            data: 'default_data'
        });

        return new Statpost(params)
            .reportData(params.dataName, params.data);
    }
});
