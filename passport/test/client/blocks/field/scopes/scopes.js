describe('Scopes field', function() {
    beforeEach(function() {
        this.block = passport.block('scopes');
        this.sinon = sinon.sandbox.create();
    });
    afterEach(function() {
        this.sinon.restore();
    });

    describe('spellTime', function() {
        _.each({
            '1 секунда': 1,
            '2 секунды': 2,
            '12 секунд': 12,
            '1 минута': 60,
            '2 минуты': 120,
            '5 минут': 60 * 5,
            '1 день': 60 * 60 * 24,
            '2 дня': 2 * 60 * 60 * 24,
            '2 дня, 8 часов': 2 * 60 * 60 * 24 + 8 * 60 * 60,
            '15 лет, 9 месяцев, 17 дней, 8 часов, 12 минут': 12 * 60 + 8 * 60 * 60 + 17 * 24 * 60 * 60 + 9 * 30 * 24 * 60 * 60 + 15 * 365 * 24 * 60 * 60
        }, function(value, description) {
            it('should return "' + description + '" for ' + value, function() {
                expect(this.block.spellTime(value)).to.be(description);
            });
        });
    });

    describe('requiresApproval', function() {
        beforeEach(function() {
            this.originalModerationStatus = this.block.getInitialModerationStatus();
            this.originalInitialScopes = this.block.getInitialScopes();

            this.initialNoModeration = 'initialNoModeration';
            this.initialWithModeration1 = 'initialWithModeration1';
            this.initialWithModeration2 = 'initialWithModeration2';
            this.initialScopes = [this.initialNoModeration, this.initialWithModeration1, this.initialWithModeration2];
            this.block.setInitialScopes(this.initialScopes);

            this.sinon.stub(this.block, 'getScopeData')
                .withArgs(this.initialNoModeration).returns({
                    requiresApproval: false
                })
                .withArgs(this.initialWithModeration1).returns({
                    requiresApproval: true
                })
                .withArgs(this.initialWithModeration2).returns({
                    requiresApproval: true
                });
        });
        afterEach(function() {
            this.block.setInitialModerationStatus(this.originalModerationStatus);
            this.block.setInitialScopes(this.originalInitialScopes);
        });

        describe('with an empty scope set', function() {
            _.each({
                'PENDING': false,
                'REJECTED': false,
                'NOT_REQUIRED': false,
                'RESOLVED': false
            }, function(isRequired, status) {
                it('should return ' + isRequired + ' if application approval status is ' + status, function() {
                    this.block.setInitialModerationStatus(status);
                    expect(this.block.requiresApproval([])).to.be(isRequired);
                });
            });
        });

        describe('with scopes matching the initial set', function() {
            _.each({
                'PENDING': true,
                'REJECTED': true,
                'NOT_REQUIRED': false,
                'RESOLVED': false
            }, function(isRequired, status) {
                it('should return ' + isRequired + ' if application approval status is ' + status, function() {
                    this.block.setInitialModerationStatus(status);
                    expect(this.block.requiresApproval(this.initialScopes)).to.be(isRequired);
                });
            });
        });

        describe('with additional scope that does not requires moderation', function() {
            beforeEach(function() {
                this.additionalScope = 'additionalScope';
                this.block.getScopeData.withArgs(this.additionalScope).returns({
                    requiresApproval: false
                });
            });

            _.each({
                'PENDING': true,
                'REJECTED': true,
                'NOT_REQUIRED': false,
                'RESOLVED': false
            }, function(isRequired, status) {
                it('should return ' + isRequired + ' if application approval status is ' + status, function() {
                    this.block.setInitialModerationStatus(status);
                    expect(this.block.requiresApproval(this.initialScopes.concat([this.additionalScope]))).to.be(isRequired);
                });
            });
        });

        describe('with additional scope that requires moderation', function() {
            beforeEach(function() {
                this.additionalScope = 'additionalScope';
                this.block.getScopeData.withArgs(this.additionalScope).returns({
                    requiresApproval: true
                });
            });

            _.each({
                'PENDING': true,
                'REJECTED': true,
                'NOT_REQUIRED': true,
                'RESOLVED': true
            }, function(isRequired, status) {
                it('should return ' + isRequired + ' if application approval status is ' + status, function() {
                    this.block.setInitialModerationStatus(status);
                    expect(this.block.requiresApproval(this.initialScopes.concat([this.additionalScope]))).to.be(isRequired);
                });
            });
        });

        describe('without all scopes from the initial set, that required moderation', function() {
            _.each({
                'PENDING': false,
                'REJECTED': false,
                'NOT_REQUIRED': false,
                'RESOLVED': false
            }, function(isRequired, status) {
                it('should return ' + isRequired + ' if application approval status is ' + status, function() {
                    this.block.setInitialModerationStatus(status);
                    expect(this.block.requiresApproval([this.initialNoModeration])).to.be(isRequired);
                });
            });
        });

        describe('without one scope from the initial set, that required moderation', function() {
            _.each({
                'PENDING': true,
                'REJECTED': true,
                'NOT_REQUIRED': false,
                'RESOLVED': false
            }, function(isRequired, status) {
                it('should return ' + isRequired + ' if application approval status is ' + status, function() {
                    this.block.setInitialModerationStatus(status);
                    expect(this.block.requiresApproval([this.initialNoModeration, this.initialWithModeration1])).to.be(isRequired);
                });
            });
        });
    });
});
