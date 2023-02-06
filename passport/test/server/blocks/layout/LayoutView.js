var expect = require('expect.js');
var sinon = require('sinon');
var _ = require('lodash');

var LayoutView = require('../../../../blocks/layout/LayoutView');
var View = require('../../../../lib/views/View');

describe('Layout View', function() {
    beforeEach(function() {
        this.tld = 'com.tr';
        this.staticPath = '/st/';
        this.lang = 'ru';
        this.track_id = 'uPachaek6yae0uuchohgu0aisaYu1ich';
        this.extra = {extra: 'params'};

        this.layout = new LayoutView(this.tld, this.staticPath, this.lang, this.track_id, this.extra);
    });

    describe('Constructor', function() {
        _.each(
            {
                'not a string': null,
                'an empty string': '',
                'a string starting with a dot': '.ru'
            },
            function(value, description) {
                it(`should throw if tld is ${description}`, function() {
                    var that = this;

                    expect(function() {
                        new LayoutView(value, that.staticPath, that.lang, that.track_id);
                    }).to.throwError(function(e) {
                        expect(e.message).to.be('Top level domain string required and should omit the dot');
                    });
                });
            }
        );

        _.each(
            {
                'not a string': null,
                'an empty string': ''
            },
            function(value, description) {
                it(`should throw if static path is ${description}`, function() {
                    var that = this;

                    expect(function() {
                        new LayoutView(that.tld, value, that.lang, that.track_id);
                    }).to.throwError(function(e) {
                        expect(e.message).to.be('StaticPath should be an url to static files root');
                    });
                });
            }
        );

        _.each(
            {
                'not a string': {},
                'one letter string': 'a',
                'a string that is too long': 'whatsoever'
            },
            function(value, description) {
                it(`should throw if lang is ${description}`, function() {
                    var that = this;

                    expect(function() {
                        new LayoutView(that.tld, that.staticPath, value, that.track_id);
                    }).to.throwError(function(e) {
                        expect(e.message).to.be('Language should be a two-letter language code');
                    });
                });
            }
        );

        it('should throw if extra params are not an object', function() {
            var that = this;

            expect(function() {
                new LayoutView(that.tld, that.staticPath, that.lang, that.track_id, 'nope');
            }).to.throwError(function(e) {
                expect(e.message).to.be('Extra parameters should be passed as an object if defined');
            });
        });
    });

    describe('compile', function() {
        it('should return tld as domain', function() {
            expect(this.layout.compile().domain).to.be(this.tld);
        });

        it('should return lang as language and config.lang', function() {
            expect(this.layout.compile().language).to.be(this.lang);
            expect(this.layout.compile().config.lang).to.be(this.lang);
        });

        it('should return static path as config.paths.static', function() {
            expect(this.layout.compile().config.paths['static']).to.be(this.staticPath);
        });

        it('should return track_id as track_id.id', function() {
            expect(this.layout.compile().track_id.id).to.be(this.track_id);
        });

        it('should merge extra params into result', function() {
            var compiled = this.layout.compile();

            _.each(this.extra, function(value, key) {
                expect(compiled).to.have.property(key, value);
            });
        });

        it('should merge subviews', function() {
            var subview = new View();

            subview.compile = sinon.stub().returns({a: 'bc'});

            this.layout.append(subview);
            expect(this.layout.compile()).to.have.property('a', 'bc');
        });
    });
});
