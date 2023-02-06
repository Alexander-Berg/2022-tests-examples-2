var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');

var TrackField = require('../../../../blocks/form/track.field');

describe('Track Field', function() {
    beforeEach(function() {
        this.lang = 'ru';

        this.trackResponse = {
            field: 'track_id',
            body: {
                id: 'asdfasdfasdfasdfasdf',
                status: 'ok'
            }
        };

        this.getTrackDeferred = when.defer();
        this.getTrackDeferred.resolve(this.trackResponse);

        this.api = {
            params: sinon
                .stub()
                .withArgs('track_id')
                .returns(this.getTrackDeferred.promise)
        };

        this.field = new TrackField();
    });

    describe('compile', function() {
        it('should call api method params with track_id', function(done) {
            var api = this.api;

            this.field
                .compile(this.lang, api)
                .then(function() {
                    expect(api.params.calledWithExactly('track_id')).to.be(true);
                    done();
                })
                .then(null, done);
        });

        it('should return track_id api returned as a value', function(done) {
            var response = this.trackResponse;

            this.field
                .compile(this.lang, this.api)
                .then(function(compiled) {
                    expect(compiled.value).to.be(response.body.id);
                    done();
                })
                .then(null, done);
        });
    });
});
