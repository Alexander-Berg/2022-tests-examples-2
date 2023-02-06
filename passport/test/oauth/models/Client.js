var expect = require('expect.js');
var _ = require('lodash');

var Client = require('../../../OAuth/models/Client');

describe('Client model', function() {
    beforeEach(function() {
        this.clientScopes = new (require('../../../OAuth/models/ScopesCollection'))();
        this.clientDefinition = {
            id: '0d66fca6b5a040aa90340eabd473db19',
            title: 'Test client',
            description: 'Client for test',
            icon: 'http://icon',
            icon_id: '3374/e0778950ab864f87bc9c49b896f5d1a0-3',
            icon_url: 'https://avatars.mdst.yandex.net/get-oauth/3374/e0778950ab864f87bc9c49b896f5d1a0-3/normal',
            homepage: 'http://homepage',
            callback: 'http://callback',
            scopes: this.clientScopes,
            create_time: 1407477045,
            secret: '0d66fca6b5a040aa90340eabd473db20',
            approval_status: 0,
            blocked: false
        };

        this.viewedByOwner = true;
        this.client = new Client(this.clientDefinition, this.viewedByOwner);
    });

    describe('constructor', function() {
        it('should not throw if clientTime is null', function() {
            var clientDefinition = this.clientDefinition;

            clientDefinition.create_time = null;
            expect(function() {
                new Client(clientDefinition, true);
            }).to.not.throwError();
        });

        it('should not throw if secret is null', function() {
            var clientDefinition = this.clientDefinition;

            clientDefinition.secret = null;
            expect(function() {
                new Client(clientDefinition, true);
            }).to.not.throwError();
        });
    });

    describe('getCreationTime', function() {
        it('should return the start of epoch if client creation time is null', function() {
            this.clientDefinition.create_time = null;
            var client = new Client(this.clientDefinition, true);

            expect(client.getCreationTime()).to.eql(new Date(0));
        });
    });

    describe('getSecret', function() {
        it('should return an empty string if secret is null', function() {
            this.clientDefinition.secret = null;
            var client = new Client(this.clientDefinition, true);

            expect(client.getSecret()).to.be('');
        });
    });

    describe('getApprovalStatus', function() {
        it('should return null if approval status is unknown for the application', function() {
            delete this.clientDefinition.approval_status;
            var client = new Client(this.clientDefinition, false);

            expect(client.getApprovalStatus()).to.be(null);
        });

        _.each(Client.APPROVAL, function(status, name) {
            it('should return "' + name + '" if application has status ' + status, function() {
                this.clientDefinition.approval_status = status;
                var client = new Client(this.clientDefinition, true);

                expect(client.getApprovalStatus()).to.be(name);
            });
        });

        it('should throw if app has an unknown approval status', function() {
            this.clientDefinition.approval_status = 10000;
            var client = new Client(this.clientDefinition, true);

            expect(function() {
                client.getApprovalStatus();
            }).to.throwError(function(err) {
                expect(err.message).to.be('Unknown approval status');
            });
        });
    });
});
