const sinon = require('sinon');
const expect = require('expect.js');
const validateAMParams = require('../../../routes/authv2/validateAMParams');

let req;

let res;

let next;

describe('#validateAmParams', () => {
    beforeEach(() => {
        req = {
            _controller: {
                getUrl() {
                    return {
                        pathname: '/am'
                    };
                }
            },
            query: {
                app_platform: 'ios'
            }
        };
        res = {
            redirect: sinon.spy()
        };
        next = sinon.spy();
    });

    describe('[valid requests]', () => {
        it('should pass valid request', () => {
            validateAMParams(req, res, next);

            expect(res.redirect.called).not.to.be.ok();
            expect(next.called).to.be.ok();
        });
    });

    describe('[invalid requests]', () => {
        it('should not pass invalid app_platform', () => {
            delete req.query.app_platform;

            validateAMParams(req, res, next);

            expect(res.redirect.called).to.be.ok();
            expect(res.redirect.getCall(0).args[0]).to.be.equal('/am/finish?status=error');
            expect(next.called).not.to.be.ok();
        });

        ['phoneconfirm'].forEach((mode) => {
            it(`should not pass ${mode} mode without uid`, () => {
                req.query.mode = mode;

                validateAMParams(req, res, next);

                expect(res.redirect.called).to.be.ok();
                expect(res.redirect.getCall(0).args[0]).to.be.equal('/am/finish?status=error');
                expect(next.called).not.to.be.ok();
            });
        });
    });
});
