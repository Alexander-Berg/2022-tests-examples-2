describe('home.yaplus', function() {
    var logger;

    beforeEach(function () {
        var sandbox = sinon.createSandbox();
        logger = sandbox.stub(home, 'error');
    });

    afterEach(function () {
        home.error.restore();
    });

    describe('getCheapest', function() {
        it('должнно вернуть YA_PLUS из основных типов подписки', function() {
            home.yaplus.getCheapest([
                'YA_PLUS',
                'KP_BASIC',
                'YA_PREMIUM'
            ]).should.equal('YA_PLUS');
        });

        it('должно вернуть KP_BASIC из основных типов подписки кроме YA_PLUS', function() {
            home.yaplus.getCheapest([
                'YA_PREMIUM',
                'KP_BASIC'
            ]).should.equal('KP_BASIC');
        });

        it('должно вернуть YA_PLUS из всех видом подписки', function() {
            home.yaplus.getCheapest([
                'YA_PLUS_3M',
                'YA_PLUS_KP',
                'YA_PLUS_KP_3M',
                'YA_PREMIUM',
                'KP_BASIC'
            ]).should.equal('YA_PLUS');
        });

        it('должно вернуть undefined и залогировать ошибку с новым типом', function() {
            expect(home.yaplus.getCheapest([
                'YA_PLUS_3M_NEW'
            ])).to.be.undefined;

            logger.should.be.calledOnce;
        });
    });

    describe('getMostExpansive', function() {
        it('должнно вернуть YA_PREMIUM из основных типов подписки', function() {
            home.yaplus.getMostExpansive([
                'YA_PLUS',
                'KP_BASIC',
                'YA_PREMIUM'
            ]).should.equal('YA_PREMIUM');
        });

        it('должно вернуть KP_BASIC из основных типов подписки кроме YA_PREMIUM', function() {
            home.yaplus.getMostExpansive([
                'YA_PLUS',
                'KP_BASIC'
            ]).should.equal('KP_BASIC');
        });

        it('должно вернуть YA_PREMIUM из всех видом подписки', function() {
            home.yaplus.getMostExpansive([
                'YA_PLUS_3M',
                'YA_PLUS_KP',
                'YA_PLUS_KP_3M',
                'YA_PREMIUM',
                'KP_BASIC'
            ]).should.equal('YA_PREMIUM');
        });

        it('должно вернуть undefined и залогировать ошибку с новым типом', function() {
            expect(home.yaplus.getMostExpansive([
                'YA_PLUS_3M_NEW'
            ])).to.be.undefined;

            logger.should.be.calledOnce;
        });
    });
});

