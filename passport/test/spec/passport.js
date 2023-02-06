describe('Passport', function() {
    describe('util', function() {
        describe('normalize', function() {
            /**
             * @type {Object<expectation, value>}
             */
            _.each(
                {
                    '': null,
                    0: 0,
                    trimming: ' trimming ',
                    'multiple spaces': 'multiple   spaces',
                    'trimming and spaces': '     trimming   and spaces    '
                },
                function(input, expectation) {
                    var name = '"' + expectation + '"';

                    if (!expectation) {
                        name = 'empty string';
                    }

                    it('should return ' + name + ' for ' + typeof input + ' "' + input + '"', function() {
                        expect(passport.util.normalize(input)).to.be(expectation);
                    });
                }
            );
        });

        describe('isEmail', function() {
            it('should return false for invalid-email!#$%^@yandex.ru', function() {
                expect(passport.util.isEmail('invalid-email!#$%^@yandex.ru')).to.be(false);
            });

            it('should return true valid-email@yandex.ru', function() {
                expect(passport.util.isEmail('valid-email@yandex.ru')).to.be(true);
            });
        });

        describe('isCorrectDate', function() {
            it('should return false for 2014-12-34', function() {
                expect(passport.util.isCorrectDate('2014-12-34')).to.be(false);
            });

            it('should return false for 2014-13-10', function() {
                expect(passport.util.isCorrectDate('2014-13-10')).to.be(false);
            });

            it('should return true 2014-01-11', function() {
                expect(passport.util.isCorrectDate('2014-01-11')).to.be(true);
            });
        });

        describe('getCookie', function() {
            beforeEach(function() {
                this.cookies = document.cookie;
                document.cookie = 'whatso=ever=eve';
            });

            afterEach(function() {
                document.cookie = this.cookies;
            });

            it('should return "ever=eve" by key "whatso"', function() {
                expect(passport.util.getCookie('whatso')).to.eql('ever=eve');
            });

            it('should return "\'\'" by key "somekey"', function() {
                expect(passport.util.getCookie('somekey')).to.eql('');
            });
        });
    });

    describe('API', function() {
        beforeEach(function() {
            this.originalTrack = passport.track_id;
            passport.track_id = 'apha3aowie4ahguivoh6ohvee3Peiwah';

            this.$PostResult = new $.Deferred();
            sinon.stub($, 'ajax').returns(this.$PostResult);
        });

        afterEach(function() {
            $.ajax.restore();
            passport.api.dropCaches();
            passport.track_id = this.originalTrack;
        });

        describe('request', function() {
            /**
             * Escapes a string to use in regexp
             * @param {string} str  String to be escaped
             * @returns {string}
             *
             * @see http://stackoverflow.com/questions/3446170/escape-string-for-use-in-javascript-regex
             */
            var escapeRegExp = function(str) {
                // eslint-disable-next-line no-useless-escape
                return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, '\\$&');
            };

            beforeEach(function() {
                this.request = passport.api.request;
                this.method = 'whatever';
                this.params = {
                    a: 'bc',
                    d: 'ef'
                };

                this.originalBasePath = passport.basePath;
                passport.basePath = 'http://passport.yandex.ru/some/secondary/path/';
            });
            afterEach(function() {
                passport.basePath = this.originalBasePath;
            });

            describe('always', function() {
                beforeEach(function() {
                    this.result = this.request(this.method, this.params);
                    this.postParams = $.ajax.firstCall ? $.ajax.firstCall.args[0] : {};
                });

                it('should trigger jquery ajax', function() {
                    expect($.ajax.calledOnce).to.be(true);
                });

                it('should trigger make a post request to the api', function() {
                    expect(this.postParams).to.have.property('type', 'POST');
                });

                it('should call jquery post with json data type', function() {
                    expect(this.postParams).to.have.property('dataType', 'json');
                });

                it('should use passport.basePath as the base of the url', function() {
                    expect(this.postParams.url).to.match(new RegExp('^' + escapeRegExp(passport.basePath)));
                });

                it('should append the method name to the base of the url', function() {
                    expect(this.postParams.url).to.match(
                        new RegExp('^' + escapeRegExp(passport.basePath) + this.method)
                    );
                });

                it('should pass the params as request data to jquery post', function() {
                    delete this.postParams.data.track_id; //Track id is always added
                    expect(this.postParams.data).to.eql(this.params);
                });

                it('should add track_id to the request data', function() {
                    expect(this.postParams.data).to.have.property('track_id', passport.track_id);
                });

                it('should return a jquery promise', function() {
                    expect(this.result).to.be.aJqueryDeferredPromise();
                });

                it('should resolve resulting $.Deferred with the response if successful', function(done) {
                    var actualResponse = {
                        iama: 'response',
                        for: 'some method'
                    };

                    this.result
                        .done(function(response) {
                            expect(response).to.eql(actualResponse);
                            done();
                        })
                        .fail(asyncFail(done, 'Deferred was expected to resolve'));

                    this.$PostResult.resolve(actualResponse);
                });

                it('should reject resulting $.Deferred if request failed', function(done) {
                    this.result.fail(done).done(asyncFail(done, 'Deferred was expected to be rejected'));

                    this.$PostResult.reject();
                });

                _.each(
                    {
                        'an empty string': '',
                        number: 1,
                        null: null,
                        boolean: true,
                        'an array': []
                    },
                    function(method, description) {
                        it('should throw if method is ' + description, function() {
                            var request = this.request;

                            expect(function() {
                                request(method, {});
                            }).to.throwException(/Method should be string or plain object/);
                        });
                    }
                );

                _.each(
                    {
                        'a string': 'this is plain wrong',
                        number: 1,
                        null: null,
                        boolean: true,
                        'an array': []
                    },
                    function(params, description) {
                        it('should throw if params is ' + description, function() {
                            var request = this.request;
                            var method = this.method;

                            expect(function() {
                                request(method, params);
                            }).to.throwException(/Params should be a plain object/);
                        });
                    }
                );
            });

            describe('with options', function() {
                describe('"abortPrevious"', function() {
                    beforeEach(function() {
                        this.getRequestStub = function() {
                            return $.extend(
                                {
                                    abort: sinon.stub()
                                },
                                new $.Deferred()
                            );
                        };

                        this.options = {abortPrevious: true};
                    });

                    it('should abort previous request to the same method', function() {
                        var firstRequest = this.getRequestStub();
                        var secondRequest = this.getRequestStub();

                        $.ajax.returns(firstRequest);
                        this.request(this.method, this.params, this.options);

                        $.ajax.returns(secondRequest);
                        this.request(this.method, {}, this.options); //Call to the same method with different params

                        expect(firstRequest.abort.calledOnce).to.be(true);
                    });
                });

                describe('"cache"', function() {
                    beforeEach(function() {
                        this.response = {iama: 'cached response'};
                        this.options = {cache: true};
                    });

                    it(
                        'should resolve with the previous api response for the request ' +
                            'with same method and params',
                        function(done) {
                            var response = this.response;

                            this.request(this.method, this.params, this.options);
                            this.$PostResult.resolve(response);

                            this.request(this.method, this.params, this.options)
                                .done(function(result) {
                                    expect(result).to.eql(response);
                                    done();
                                })
                                .fail(asyncFail(done, 'Expected the request to resolve'));
                        }
                    );

                    it('should not make additional requests when called with same method and params', function() {
                        this.request(this.method, this.params, this.options);
                        this.request(this.method, this.params, this.options);
                        expect($.ajax.calledOnce).to.be(true);
                    });

                    it('should wait for the previous request for the same method and params to resolve', function() {
                        var firstRequest = new $.Deferred();
                        var secondRequest = new $.Deferred();

                        expect(secondRequest.state()).to.be('pending');

                        $.ajax.returns(firstRequest);
                        this.request(this.method, this.params, this.options);

                        $.ajax.returns(secondRequest);
                        var secondResult = this.request(this.method, this.params, this.options);

                        expect(secondResult.state()).to.be('pending');
                        firstRequest.resolve({});

                        expect(secondResult.state()).to.be('resolved');
                    });

                    it('should clone cached data to avoid changing it as an object', function(done) {
                        var first = this.request(this.method, this.params, this.options);
                        var second = this.request(this.method, this.params, this.options);

                        this.$PostResult.resolve({});

                        var fail = asyncFail(done, 'Expected to resolve');

                        first
                            .done(function(result) {
                                result.field = 'whaaa?';

                                second
                                    .done(function(otherResult) {
                                        expect(otherResult).to.not.have.property('field');
                                        done();
                                    })
                                    .fail(fail);
                            })
                            .fail(fail);
                    });
                });
            });
        });

        describe('log', function() {
            beforeEach(function() {
                window.uid = '123';

                this._originals = {
                    logger_token: passport.logger_token,
                    track_id: passport.track_id
                };
                passport.logger_token = 'paewaing2OoL5neepeip1mee8vaa4oo4';
                passport.track_id = 'aen4pheemei4ieshaitievee9pohQu1i';

                this.message = 'heyhey, I am a log message';
                sinon.stub(passport.api, 'request');
                passport.api.log(this.message);
            });
            afterEach(function() {
                passport.logger_token = this._originals.logger_token;
                passport.track_id = this._originals.track_id;
                passport.api.request.restore();
                delete window.uid;
            });

            it('should call request', function() {
                expect(passport.api.request.calledOnce).to.be(true);
            });

            it('should call request with logger as a method', function() {
                expect(passport.api.request.calledWith('logger')).to.be(true);
            });

            it('should call encode if was called with encode=true option', function() {
                sinon.stub(window.simpleCipher, 'encode');
                passport.api.log(this.message, {encrypt: true});
                expect(window.simpleCipher.encode.calledOnce).to.be(true);
                window.simpleCipher.encode.restore();
            });

            it('should call encode with track_id if was called with encode=true option', function() {
                sinon.stub(window.simpleCipher, 'encode');
                passport.api.log(this.message, {encrypt: true});
                var track_id = window.simpleCipher.encode.firstCall.args[0];

                expect(track_id).to.be(passport.track_id);
                window.simpleCipher.encode.restore();
            });

            describe('request params', function() {
                beforeEach(function() {
                    this.params = passport.api.request.firstCall.args[1];
                    this.json = JSON.parse(this.params.log);
                });

                it('should contain object with log prop', function() {
                    expect(this.params).to.have.property('log');
                });

                it('should contain action', function() {
                    expect(this.json).to.have.property('action', this.message);
                });

                it('should contain loglevel: info', function() {
                    expect(this.json).to.have.property('loglevel', 'info');
                });

                it('should contain loglevel if it was provided in options', function() {
                    var loglevel = 'warning';

                    passport.api.log(this.message, {loglevel: loglevel});
                    var params = passport.api.request.secondCall.args[1];
                    var json = JSON.parse(params.log);

                    expect(json).to.have.property('loglevel', loglevel);
                });

                it('should contain track', function() {
                    expect(this.json).to.have.property('track_id', passport.track_id);
                });

                it('should contain logger token', function() {
                    expect(this.json).to.have.property('token', passport.logger_token);
                });

                it('should contain window url', function() {
                    expect(this.json).to.have.property('url', window.location.href);
                });

                it('should contain timestamp', function() {
                    expect(this.json).to.have.property('ev_tsf');
                });

                it('should contain uid', function() {
                    expect(this.json).to.have.property('uid', '123');
                });
            });
        });
    });
});
