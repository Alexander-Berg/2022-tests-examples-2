var expect = require('expect.js');
var sinon = require('sinon');

var metrics = require('../../../routes/metrics');

describe('Metrics', function() {
    it('should instantiate Metrics with the given config', function() {
        var config = {whatso: 'ever'};

        sinon.spy(metrics, 'Metrics');

        metrics(config);

        expect(metrics.Metrics.calledOnce).to.be(true);
        expect(metrics.Metrics.calledWithExactly(config)).to.be(true);

        metrics.Metrics.restore();
    });

    describe('getCounterID', function() {
        beforeEach(function() {
            this.config = {
                '/registration': 'registrationCounterID',
                '/registration/mail': 'mailCounter',
                '/registration/mail/digit': 'mailDigitsCounter'
            };

            this.metrics = new metrics.Metrics(this.config);
        });

        it('should return id from config for exactly matching urls', function() {
            expect(this.metrics.getCounterID('/registration')).to.be(this.config['/registration']);
        });

        it('should return id from config for the parent url, if no exactly matching url found', function() {
            expect(this.metrics.getCounterID('/registration/simple')).to.be(this.config['/registration']);
        });

        it('should return id from the most specific parent url in config', function() {
            expect(this.metrics.getCounterID('/registration/mail/unknown')).to.be(this.config['/registration/mail']);
        });

        it('should return null for an url that has no exact match nor matching parent urls in config', function() {
            expect(this.metrics.getCounterID('/profile/address/registration/mail')).to.be(null);
        });

        it('should return / instead of null if / value is defined', function() {
            this.config['/'] = 'DefaultCounterID';
            this.metrics = new metrics.Metrics(this.config);

            expect(this.metrics.getCounterID('/profile/access')).to.be(this.config['/']);
        });
    });

    describe('route', function() {
        beforeEach(function() {
            this.route = metrics({
                '/some': 'config'
            });

            this.req = {
                url: 'someUrl'
            };
            this.res = {
                locals: {}
            };
            this.next = sinon.spy();
        });

        it('should call for metrics.getCounterID with url from req parameter', function() {
            sinon.spy(metrics.Metrics.prototype, 'getCounterID');

            this.route(this.req, this.res, this.next);
            expect(metrics.Metrics.prototype.getCounterID.calledWithExactly(this.req.url)).to.be(true);
            metrics.Metrics.prototype.getCounterID.restore();
        });

        it('should set metrics_id in locals with the value from metrics.getCounterID', function() {
            var counterID = 'whatsoever';

            sinon.stub(metrics.Metrics.prototype, 'getCounterID').returns(counterID);

            this.route(this.req, this.res, this.next);
            expect(this.res.locals.metrics_id === counterID).to.be(true);

            metrics.Metrics.prototype.getCounterID.restore();
        });
    });
});
