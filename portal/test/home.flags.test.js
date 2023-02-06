describe('home.flags', function() {
    const mock = require('mock-fs');
    const path = require('path');
    before(function () {
        const fakeFlags = path.resolve(__dirname, '../../../test_flags.json');

        mock({
            [fakeFlags]: JSON.stringify({
                'test_flag': {
                    'date': '26.03.2019',
                    'description': 'HOME-0: Флаг для примера заполнения файла и тестов',
                    'manager': '4eb0da',
                    'expire': '01.01.2219'
                }
            })
        });
        home.flags.setDesc('test_flags.json');
    });

    after(function () {
        mock.restore();
    });

    describe('get', function() {
        before(function () {
            sinon.spy(home, 'error');
        });

        after(function () {
            home.error.restore();
        });

        it('handles empty data', function() {
            expect(home.flags.get({}, 'test_flag')).to.be.undefined;

            expect(home.flags.get({
                ab_flags: null
            }, 'test_flag')).to.be.undefined;

            expect(home.flags.get({
                ab_flags: {}
            }, 'test_flag')).to.be.undefined;

            expect(home.flags.get({
                ab_flags: {
                    test_flag: {}
                }
            }, 'test_flag')).to.be.undefined;
        });

        it('handles default value', function() {
            home.flags.get({}, 'test_flag', 'red').should.equal('red');

            home.flags.get({
                ab_flags: null
            }, 'test_flag', 'red').should.equal('red');

            home.flags.get({
                ab_flags: {}
            }, 'test_flag', 'red').should.equal('red');

            home.flags.get({
                ab_flags: {
                    test_flag: {}
                }
            }, 'test_flag', 'red').should.equal('red');

            home.flags.get({
                ab_flags: {
                    test_flag: {
                        value: 'blue'
                    }
                }
            }, 'test_flag', 'red').should.equal('blue');
        });

        it('handles missing description', function() {
            expect(home.flags.get({}, 'missing_flag')).to.be.undefined;
            home.error.should.have.been.calledOnce;
            home.error.should.have.been.calledWith('Missing "missing_flag" flag description, update flags_allowed.json');
        });

        it('handles enabled flag', function() {
            home.flags.get({
                ab_flags: {
                    test_flag: {
                        value: ''
                    }
                }
            }, 'test_flag').should.equal('');

            home.flags.get({
                ab_flags: {
                    test_flag: {
                        value: 'yellow'
                    }
                }
            }, 'test_flag').should.equal('yellow');

            home.flags.get({
                ab_flags: {
                    test_flag: {
                        value: 234
                    }
                }
            }, 'test_flag').should.equal(234);
        });
    });

    describe('checkBool', function() {
        before(function () {
            sinon.spy(home, 'error');
        });

        after(function () {
            home.error.restore();
        });

        it('handles missing description', function() {
            home.flags.checkBool({}, 'missing_flag').should.be.false;
            home.error.should.have.been.calledOnce;
            home.error.should.have.been.calledWith('Missing "missing_flag" flag description, update flags_allowed.json');
        });

        it('handles enabled flag', function() {
            home.flags.checkBool({
                ab_flags: {
                    test_flag: {
                        value: ''
                    }
                }
            }, 'test_flag').should.equal(false);

            home.flags.checkBool({
                ab_flags: {
                    test_flag: {
                        value: 'no'
                    }
                }
            }, 'test_flag').should.equal(false);

            home.flags.checkBool({
                ab_flags: {
                    test_flag: {
                        value: 'yes'
                    }
                }
            }, 'test_flag').should.equal(false);

            home.flags.checkBool({
                ab_flags: {
                    test_flag: {
                        value: '1'
                    }
                }
            }, 'test_flag').should.equal(true);

            home.flags.checkBool({
                ab_flags: {
                    test_flag: {
                        value: 1
                    }
                }
            }, 'test_flag').should.equal(true);
        });
    });
});

