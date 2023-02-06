var expect = require('expect.js');

var Configurator = require('../logger/Configurator');

describe('Configurator', function() {
    beforeEach(function() {
        this.config = Configurator.instance();
    });

    describe('static', function() {
        describe('knownLevels', function() {
            it('should be an array of levels', function() {
                expect(Configurator.knownLevels).to.be.an(Array);
                Configurator.knownLevels.forEach(function(level) {
                    expect(level).to.be.a('string');
                });
            });
        });

        describe('instance', function() {
            it('should be a function', function() {
                expect(Configurator.instance).to.be.a('function');
            });

            it('should always return the same instance of configurator', function() {
                expect(Configurator.instance()).to.be(Configurator.instance());
            });
        });
    });

    describe('minLevel', function() {
        it('should throw if given an unknown level', function() {
            var config = this.config;

            expect(function() {
                config.minLevel('unknown');
            }).to.throwError(function(err) {
                expect(err.message).to.be('Unknown loglevel unknown');
            });
        });

        it('should return the config itself for chaining', function() {
            expect(this.config.minLevel(this.config.getCurrentMinLevel())).to.be(this.config);
        });
    });

    describe('levelImportantEnough', function() {
        it('should throw if given an unknown level', function() {
            var config = this.config;

            expect(function() {
                config.levelImportantEnough('unknown');
            }).to.throwError(function(err) {
                expect(err.message).to.be('Unknown loglevel unknown');
            });
        });

        it('should return true for all levels above current minLevel', function() {
            var minLevelIndex = Math.floor(Configurator.knownLevels.length / 2);

            this.config.minLevel(Configurator.knownLevels[minLevelIndex]);

            for (var i = 0; i <= minLevelIndex; i++) {
                expect(this.config.levelImportantEnough(Configurator.knownLevels[i])).to.be(true);
            }
        });

        it('should return false for all levels below current minLevel', function() {
            var minLevelIndex = Math.floor(Configurator.knownLevels.length / 2);

            this.config.minLevel(Configurator.knownLevels[minLevelIndex]);

            for (var i = minLevelIndex + 1; i < Configurator.knownLevels.length; i++) {
                expect(this.config.levelImportantEnough(Configurator.knownLevels[i])).to.be(false);
            }
        });
    });

    describe('logIdRquiredForLevel', function() {
        it('should throw if given an unknown level', function() {
            var config = this.config;

            expect(function() {
                config.logIdRquiredForLevel('unknown');
            }).to.throwError(function(err) {
                expect(err.message).to.be('Unknown loglevel unknown');
            });
        });

        it('should return true for all levels above "info"', function() {
            var i = -1;
            var infoIndex = Configurator.knownLevels.indexOf('info');

            while (infoIndex >= ++i) {
                expect(this.config.logIdRquiredForLevel(Configurator.knownLevels[i])).to.be(true);
            }
        });

        it('should return false for all levels below info', function() {
            var i = Configurator.knownLevels.length;
            var infoIndex = Configurator.knownLevels.indexOf('info');

            while (infoIndex < --i) {
                expect(this.config.logIdRquiredForLevel(Configurator.knownLevels[i])).to.be(false);
            }
        });
    });

    describe('setFormatter', function() {
        it('should set formatter', function() {
            var formatter = this.config.getFormatterByName('production');

            expect(this.config.setFormatter(formatter).getFormatter()).to.be(formatter);
        });
    });

    describe('setHandler', function() {
        it('should set handler', function() {
            var handler = this.config.getHandlerByName('buffering');

            expect(this.config.setHandler(handler).getHandler()).to.be(handler);
        });
    });
});
