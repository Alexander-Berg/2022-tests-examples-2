var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');
var reqRes = require('pcontroller/tools/expressReqRes');
var defaultLang = 'en';
var defaultLanglist = [
    {id: 'ru', name: 'Ru'},
    {id: 'en', name: 'En'},
    {id: 'uk', name: 'Ua'}
];

describe('Controller', function() {
    beforeEach(function() {
        this.req = reqRes.req();
        this.res = reqRes.res();

        this.logId = 'siuH2sheabuquocoo4faed1utui8aete';

        this.api = {};
        this.realApi = require('../../../../lib/passport-api/index');
        sinon.stub(this.realApi, 'client').returns(when.resolve(this.api));

        this.Controller = require('../../../../lib/controller');
        this.controller = new this.Controller(this.req, this.res, this.logId);

        //Used to create an api
        sinon.stub(this.controller, 'getRequestParam');

        sinon.stub(this.controller, 'getLangdetect').returns(
            when.resolve({
                id: defaultLang,
                name: defaultLang,
                list: defaultLanglist
            })
        );
    });

    afterEach(function() {
        this.realApi.client.restore();
    });

    describe('getLanguage', function() {
        it('should resolve with the language from getLangdetect method response', function(done) {
            this.controller
                .getLanguage()
                .then(function(lang) {
                    expect(lang).to.be(defaultLang);
                    done();
                })
                .then(null, done);
        });

        it('should resolve with "ru" if response was indeterminate', function(done) {
            this.controller.getLangdetect.restore();
            sinon.stub(this.controller, 'getLangdetect').returns(when.resolve({}));

            this.controller
                .getLanguage()
                .then(function(lang) {
                    expect(lang).to.be('ru');
                    done();
                })
                .then(null, done);
        });
    });

    describe('getLanglist', function() {
        it('should resolve with the list from getLangdetect method response', function(done) {
            this.controller
                .getLanglist()
                .then(function(list) {
                    expect(list).to.be(defaultLanglist);
                    done();
                })
                .then(null, done);
        });

        it('should resolve with empty array if response was indeterminate', function(done) {
            this.controller.getLangdetect.restore();
            sinon.stub(this.controller, 'getLangdetect').returns(when.resolve({}));

            this.controller
                .getLanglist()
                .then(function(list) {
                    expect(list).to.eql([]);
                    done();
                })
                .then(null, done);
        });
    });

    describe('suggestGender', function() {
        beforeEach(function() {
            this.genderResponse = {
                field: 'gender',
                body: {
                    status: 'ok',
                    gender: 'male'
                }
            };

            this.api.suggestGender = sinon.stub().returns(when.resolve(this.genderResponse));
            this.firstname = 'Вася';
            this.lastname = 'Эпифанцева';
        });

        it('should call api.suggestGender with firstname and lastname', function(done) {
            var that = this;

            this.controller
                .suggestGender(this.firstname, this.lastname)
                .then(function() {
                    expect(that.api.suggestGender.calledOnce).to.be(true);
                    expect(that.api.suggestGender.firstCall.args[0]).to.eql({
                        firstname: that.firstname,
                        lastname: that.lastname
                    });
                    done();
                })
                .then(null, done);
        });

        it('should return the gender from the api response', function(done) {
            var that = this;

            this.controller
                .suggestGender(this.firstname, this.lastname)
                .then(function(gender) {
                    expect(gender).to.be(that.genderResponse.body.gender);
                    done();
                })
                .then(null, done);
        });

        it('should return "unknown" if api failed to respond', function(done) {
            this.api.suggestGender.returns(when.reject());
            this.controller
                .suggestGender(this.firstname, this.lastname)
                .then(function(gender) {
                    expect(gender).to.be('unknown');
                    done();
                })
                .then(null, done);
        });

        [
            {}, //tests no body
            {body: {gender: null}} //tests gender is undefined
        ].forEach(function(indeterminateResponse) {
            it(`should return "unknown" if api response was ${JSON.stringify(indeterminateResponse)}`, function(done) {
                this.api.suggestGender.returns(when.resolve(indeterminateResponse));
                this.controller
                    .suggestGender(this.firstname, this.lastname)
                    .then(function(gender) {
                        expect(gender).to.be('unknown');
                        done();
                    })
                    .then(null, done);
            });
        });
    });

    describe('followRetpath', function() {
        beforeEach(function() {
            this.retpath = 'https://google.com/conquers/the/world';
            this.validatedRetpath = '//yandex.ru';
            this.controller.getRequestParam.returns(this.retpath);
            sinon.stub(this.controller, 'validateRetpath').returns(when.resolve(this.validatedRetpath));
            sinon.stub(this.controller, 'redirect');
            sinon.stub(this.controller, 'redirectToFrontpage');
        });

        it('should check retpath is valid', function(done) {
            var that = this;

            this.controller
                .followRetpath()
                .then(function() {
                    expect(that.controller.validateRetpath.calledWithExactly(that.retpath)).to.be(true);
                    expect(that.controller.validateRetpath.calledAfter(that.controller.getRequestParam)).to.be(true);
                    done();
                })
                .then(null, done);
        });

        it('should redirect to retpath if it is valid', function(done) {
            var that = this;

            this.controller
                .followRetpath()
                .then(function() {
                    expect(that.controller.redirect.calledWithExactly(that.validatedRetpath)).to.be(true);
                    expect(that.controller.redirect.calledAfter(that.controller.validateRetpath)).to.be(true);
                    expect(that.controller.redirectToFrontpage.called).to.be(false);
                    done();
                })
                .then(null, done);
        });

        it('should redirect to frontpage if retpath is not valid', function(done) {
            var that = this;

            this.controller.validateRetpath.returns(when.resolve(null));
            this.controller
                .followRetpath()
                .then(function() {
                    expect(that.controller.redirect.called).to.be(false);
                    expect(that.controller.redirectToFrontpage.calledAfter(that.controller.validateRetpath)).to.be(
                        true
                    );
                    done();
                })
                .then(null, done);
        });
    });

    describe('validateRetpath', function() {
        beforeEach(function() {
            this.retpath = 'http://yandex.ru';
            this.validatedRetpath = '//yandex.ru';
            this.api.validateRetpath = sinon.stub().returns(
                when.resolve({
                    field: 'retpath',
                    body: {
                        status: 'ok',
                        retpath: this.validatedRetpath
                    }
                })
            );
        });

        it('should call api method validateRetpath with given retpath', function(done) {
            var api = this.api;
            var retpath = this.retpath;

            this.controller
                .validateRetpath(this.retpath)
                .then(function() {
                    expect(api.validateRetpath.calledOnce).to.be(true);
                    expect(api.validateRetpath.firstCall.args[0].retpath).to.be(retpath);
                    done();
                })
                .then(null, done);
        });

        it('should resolve with validated retpath api returned if api said retpath is valid', function(done) {
            var validated = this.validatedRetpath;

            this.controller
                .validateRetpath(this.retpath)
                .then(function(retpath) {
                    expect(retpath).to.be(validated);
                    done();
                })
                .then(null, done);
        });

        it('should resolve with null if responded with validation_errors', function(done) {
            this.api.validateRetpath.returns(
                when.resolve({
                    field: 'retpath',
                    body: {
                        status: 'ok',
                        validation_errors: [
                            {
                                field: 'retpath',
                                message: 'Url "//zyltrc.ru" is not in allowed hosts range',
                                code: 'notin'
                            }
                        ]
                    }
                })
            );

            this.controller
                .validateRetpath(this.retpath)
                .then(function(retpath) {
                    expect(retpath).to.be(null);
                    done();
                })
                .then(null, done);
        });
    });

    describe('redirectToFrontpage', function() {
        it('should call controller.redirect with /profile/', function() {
            sinon.stub(this.controller, 'redirectToLocalUrl');
            this.controller.redirectToFrontpage();
            expect(this.controller.redirectToLocalUrl.calledWithExactly({pathname: 'profile'})).to.be(true);
        });
    });

    describe('decodePunycodeEmails', function() {
        it('should decode punycode emails', function() {
            var emails = {
                'foo@bar': 'foo@bar',
                'foo@xn--e1aybc.xn--p1ai': 'foo@тест.рф'
            };

            var decodedEmails = this.controller.decodePunycodeEmails(emails);

            Object.keys(decodedEmails).forEach(function(email) {
                expect(email).to.be(decodedEmails[email]);
            });
        });
    });

    describe('encodeEmailToPunycode', function() {
        it('should encode email domain to punycode', function() {
            var emails = [
                {
                    original: 'foo@bar.com',
                    encoded: 'foo@bar.com'
                },
                {
                    original: 'foo@тест.рф',
                    encoded: 'foo@xn--e1aybc.xn--p1ai'
                },
                {
                    original: 'foo@xn--e1aybc.xn--p1ai',
                    encoded: 'foo@xn--e1aybc.xn--p1ai'
                },
                {
                    original: 'foobar.com',
                    encoded: 'foobar.com'
                }
            ];

            emails.forEach(function(email) {
                expect(this.controller.encodeEmailToPunycode(email.original)).to.be(email.encoded);
            }, this);
        });

        it('should throw if email is invalid punycode', function() {
            var email = 'abc@xn--11.xn--11';

            expect(this.controller.encodeEmailToPunycode)
                .withArgs(email)
                .to.throwException();
        });
    });

    describe('writeStatbox', function() {
        it('should call the api method statboxLogger with the data from args', function(done) {
            var api = this.api;

            api.statboxLogger = sinon.stub();

            var data = {};

            this.controller
                .writeStatbox(data)
                .then(function() {
                    expect(api.statboxLogger.calledOnce).to.be(true);
                    expect(api.statboxLogger.calledWithExactly(data)).to.be(true);
                    done();
                })
                .then(null, done);
        });

        it('should resolve with what api.statboxLogger resolves with', function(done) {
            var resolution = {};

            this.api.statboxLogger = sinon.stub().returns(when.resolve(resolution));
            this.controller
                .writeStatbox()
                .then(function(result) {
                    expect(result).to.be(resolution);
                    done();
                })
                .then(null, done);
        });
    });

    describe('readTrack', function() {
        beforeEach(function() {
            this.api.track = sinon.stub();

            this.trackResponse = {
                field: 'track',
                body: {
                    status: 'ok',
                    field1: 'data1',
                    field2: 'data2'
                }
            };
            this.api.readTrack = sinon.stub().returns(when.resolve(this.trackResponse));
        });

        // it('should throw if called with track that is not a string', function() {
        //     var readTrack = this.controller.readTrack;
        //     expect(function() {
        //         readTrack({});
        //     }).to.throwError(function(e) {
        //         expect(e.message).to.be('Track should be a string');
        //     });
        // });

        it('should set track before calling api.readTrack if called with track', function(done) {
            var api = this.api;
            var track = 'ivi6wee0quahjoceef7oopu8sahGhai7';

            this.controller
                .readTrack(track)
                .then(function() {
                    expect(api.track.calledOnce).to.be(true);
                    expect(api.track.calledWithExactly(track)).to.be(true);
                    expect(api.track.calledBefore(api.readTrack)).to.be(true);
                    done();
                })
                .then(null, done);
        });

        it('should not call api.track if called without track', function(done) {
            var api = this.api;

            this.controller
                .readTrack()
                .then(function() {
                    expect(api.track.called).to.be(false);
                    done();
                })
                .then(null, done);
        });

        it('should resolve with the response.body of the data api.readTrack resolved with', function(done) {
            var that = this;

            this.controller
                .readTrack()
                .then(function(track) {
                    expect(track).to.be(that.trackResponse.body);
                    done();
                })
                .then(null, done);
        });

        it('should reject with an error if response.body.status was not ok', function(done) {
            this.trackResponse.body.status = 'error';
            this.api.readTrack.returns(when.resolve(this.trackResponse));
            this.controller
                .readTrack()
                .then(asyncFail(done, 'expected the promise to be rejected'), function(error) {
                    expect(error.message).to.be('Reading track status was not "ok"');
                    done();
                })
                .then(null, done);
        });
    });

    describe('deleteTrack', function() {
        beforeEach(function() {
            this.api.track = sinon.stub();
            this.api.delTrack = sinon.stub().returns(when.resolve());
        });
        // it('should throw if called with track that is not a string', function() {
        //     expect(function() {
        //         this.controller.deleteTrack({});
        //     }).to.throwError(function(e) {
        //         expect(e.message).to.be('Track should be a string');
        //     });
        // });

        it('should set track before calling api.delTrack if called with track', function(done) {
            var api = this.api;
            var track = 'ivi6wee0quahjoceef7oopu8sahGhai7';

            this.controller
                .deleteTrack(track)
                .then(function() {
                    expect(api.track.calledOnce).to.be(true);
                    expect(api.track.calledWithExactly(track)).to.be(true);
                    expect(api.track.calledBefore(api.delTrack)).to.be(true);
                    done();
                })
                .then(null, done);
        });

        it('should not call api.track if called without track', function(done) {
            var api = this.api;

            this.controller
                .deleteTrack()
                .then(function() {
                    expect(api.track.called).to.be(false);
                    done();
                })
                .then(null, done);
        });

        it('should call api.delTrack', function(done) {
            var api = this.api;

            this.controller
                .deleteTrack()
                .then(function() {
                    expect(api.delTrack.calledOnce).to.be(true);
                    done();
                })
                .then(null, done);
        });
    });

    describe('writeTrack', function() {
        beforeEach(function() {
            this.api.writeTrack = sinon.stub().returns(when.resolve());

            this.retpathErrorRejectionReason = [
                {
                    field: 'retpath',
                    message: 'Url "//zyltrc.ru" is not in allowed hosts range',
                    code: 'notin'
                }
            ];

            this.invalidTrackRejectionReason = [
                {
                    field: 'track_id',
                    message: 'Invalid track id value',
                    code: 'invalidid'
                }
            ];

            this.dataToWrite = {
                retpath: 'http://mail.yandex.ru',
                origin: 'hostroot_totally_better_than_safe',
                service: 'mail'
            };
        });

        // it('should throw if called with anything but plain object', function() {
        //     var writeTrack = this.controller.writeTrack;
        //     expect(function() {
        //         writeTrack('throw me');
        //     }).to.throwError(function(e) {
        //         expect(e.message).to.be('Data to be written into track should be a plain object');
        //     });
        // });

        it('should resolve without calling writeTrack if called with an empty plain object', function(done) {
            var that = this;

            this.controller
                .writeTrack({})
                .then(function() {
                    expect(that.api.writeTrack.called).to.be(false);
                    done();
                })
                .then(null, done);
        });

        it('should delete retpath and repeat the attempt, if there was an error with retpath', function(done) {
            sinon.spy(this.controller, 'writeTrack');
            var writeTrack = this.api.writeTrack;
            var dataToWrite = this.dataToWrite;

            writeTrack
                .onCall(0)
                .returns(when.reject(this.retpathErrorRejectionReason))
                .onCall(1)
                .returns(when.resolve());

            this.controller
                .writeTrack(dataToWrite)
                .then(function() {
                    expect(writeTrack.calledTwice).to.be(true);
                    //First time, data should be equal to the original
                    expect(writeTrack.firstCall.args[0]).to.eql(dataToWrite);

                    var secondCallData = writeTrack.secondCall.args[0];

                    expect(secondCallData).to.not.have.property('retpath');
                    _(dataToWrite)
                        .omit('retpath')
                        .each(function(value, key) {
                            //Second time, data is all the original has, but retpath
                            expect(secondCallData[key]).to.be(value);
                        });

                    done();
                })
                .then(null, done);
        });

        it(
            'should resolve with what the second attempt to write track resolves with ' +
                'if there was an error with retpath',
            function(done) {
                var secondAttemptResolution = {};

                this.api.writeTrack
                    .onCall(0)
                    .returns(when.reject(this.retpathErrorRejectionReason))
                    .onCall(1)
                    .returns(when.resolve(secondAttemptResolution));

                this.controller
                    .writeTrack(this.dataToWrite)
                    .then(function(resolution) {
                        expect(resolution).to.be(secondAttemptResolution);
                        done();
                    })
                    .then(null, done);
            }
        );

        it('should reject with an error api returned, if the error was not about the retpath', function(done) {
            var invalidTrackRejectionReason = this.invalidTrackRejectionReason;

            this.api.writeTrack.returns(when.reject(invalidTrackRejectionReason));
            this.controller
                .writeTrack(this.dataToWrite)
                .then(asyncFail(done, 'Expected the promise to be rejected'), function(error) {
                    expect(error).to.be(invalidTrackRejectionReason);
                    done();
                })
                .then(null, done);
        });
    });
});
