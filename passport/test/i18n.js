var expect = require('expect.js');
var sinon = require('sinon');
var _ = require('lodash');

var i18n = require('../libs/i18n');

describe('i18n', function() {
    beforeEach(function() {
        this.origGetTranslations = i18n.getTranslations;
        i18n.getTranslations = sinon.stub().returns({a: 'bc'});
    });
    afterEach(function() {
        i18n.getTranslations = this.origGetTranslations;
        i18n.reset();
    });

    _.each(
        {
            null: null,
            'a boolean': true,
            'a number': 1,
            'one symbol long': 'r',
            'over two symbols long': 'rus',
            'an object': {}
        },
        function(value, description) {
            it('should throw if lang is ' + description, function() {
                expect(function() {
                    i18n(value, 'key');
                }).to.throwError(function(e) {
                    expect(e.message).to.be('Lang should be a two-letter language code');
                });
            });
        }
    );

    _.each(
        {
            null: null,
            'a boolean': true,
            'a number': 1,
            'an empty string': '',
            'an object': {}
        },
        function(value, description) {
            it('should throw if key is ' + description, function() {
                expect(function() {
                    i18n('ru', value);
                }).to.throwError(function(e) {
                    expect(e.message).to.be('Key should be a string');
                });
            });
        }
    );

    it('should get translations by language', function() {
        i18n('ru', 'a');
        expect(i18n.getTranslations.calledOnce).to.be(true);
        expect(i18n.getTranslations.calledWithExactly('ru')).to.be(true);
    });

    it('should return a translation', function() {
        expect(i18n('ru', 'a')).to.be('bc');
    });

    it(
        'should ignore first symbol of a key, if it is a percent that is not a replacement ' +
            'combination (not followed by a digit)',
        function() {
            expect(i18n('ru', '%a')).to.be('bc');
        }
    );

    it('should substitute %n to a respective argument', function() {
        i18n.getTranslations.returns({key: '%1'});
        expect(i18n('ru', 'key', 'substitution')).to.be('substitution');
    });

    it("should substitute multiple %n's to respoective arguments", function() {
        i18n.getTranslations.returns({key: '%1 is %2'});
        expect(i18n('ru', 'key', 'substitution', 'good')).to.be('substitution is good');
    });

    it('should throw if there is not enough arguments for every replacement', function() {
        i18n.getTranslations.returns({key: '%1 is %2'});
        expect(function() {
            i18n('ru', 'key', 'substitution');
        }).to.throwError(function(e) {
            expect(e.message).to.be('Substitution failed: not enough arguments');
        });
    });

    it('should throw if key is unknown', function() {
        var unknownKey = 'unknown_key';

        expect(function() {
            i18n('ru', unknownKey);
        }).to.throwError(function(e) {
            expect(e.message).to.be('Unknown localization key: ' + unknownKey);
        });
    });

    it('should not throw if key exists but is empty', function() {
        i18n.getTranslations.returns({key: ''});
        expect(function() {
            i18n('ru', 'key');
        }).to.not.throwError();
    });

    it('should throw if no keysets were loaded', function() {
        i18n.getTranslations = this.origGetTranslations;
        i18n.setAllowedLangs(['ru']);
        i18n.setKeysets(['smth']);

        expect(function() {
            i18n('ru', 'key');
        }).to.throwError(function(e) {
            expect(e.message).to.be('Localization files should be loaded with i18n.loadFromDir()');
        });
    });

    describe('getTranslations', function() {
        beforeEach(function() {
            i18n.setAllowedLangs(['ru']);
            i18n.setKeysets(['another']);
            i18n.setKeysets(['keyset']);
            i18n.loadFromDir(__dirname + '/localizations');
            i18n.getTranslations = this.origGetTranslations;
        });

        it('should return merged contents of localization jsons', function() {
            expect(i18n.getTranslations('ru')).to.eql({
                definition: 'translation',
                blah: 'bla-blah'
            });
        });

        it('should silently load russian translation if lang is not in allowed list', function() {
            expect(i18n.getTranslations('en')).to.not.have.property('definition', 'this here is unallowed');
        });

        it('should return translations loaded with extra call to loadFromDir', function() {
            i18n.loadFromDir(__dirname + '/extraLocalizations');
            expect(i18n.getTranslations('ru')).to.eql({
                definition: 'translation',
                blah: 'bla-blah',
                extra: 'Этот файл загружается дополнительным вызовом к .loadFromDir'
            });
        });
    });

    describe('setAllowedLangs', function() {
        _.each(
            {
                null: null,
                'a boolean': true,
                'a number': 1,
                'a single lang code': 'ru',
                'an object': {},
                'an empty array': [],
                'an array with a string that is not a lang code': ['r'],
                'an array with anything but lang codes': ['ru', 1, 'en']
            },
            function(value, description) {
                it('should throw if allowed langs is ' + description, function() {
                    expect(function() {
                        i18n.setAllowedLangs(value);
                    }).to.throwError(function(e) {
                        expect(e.message).to.be('Langs should be an array of two-letter language codes');
                    });
                });
            }
        );

        it('should return i18n for chaining', function() {
            expect(i18n.setAllowedLangs(['ru'])).to.be(i18n);
        });
    });

    describe('setKeysets', function() {
        _.each(
            {
                null: null,
                'a boolean': true,
                'a number': 1,
                'a single string': 'ru',
                'an object': {},
                'an empty array': [],
                'an array with anything but strings': ['ru', 1, 'en']
            },
            function(value, description) {
                it('should throw if keysets is ' + description, function() {
                    expect(function() {
                        i18n.setKeysets(value);
                    }).to.throwError(function(e) {
                        expect(e.message).to.be(
                            'Keysets should be an array of keyset names matching the keyset part in the ' +
                                'filename (Common for Common.ru.json)'
                        );
                    });
                });
            }
        );

        it('should return i18n for chaining', function() {
            expect(i18n.setKeysets(['common'])).to.be(i18n);
        });
    });

    describe('loadFromDir', function() {
        beforeEach(function() {
            i18n.setAllowedLangs(['ru']);
            i18n.setKeysets(['another', 'keyset']);
        });

        _.each(
            {
                null: null,
                'a boolean': true,
                'a number': 1,
                'an object': {},
                'an empty array': [],
                'a root dir reference': '/',
                'a nonexistent directory': __dirname + '/nonexistent'
            },
            function(value, description) {
                it('should throw if localizations dir is ' + description, function() {
                    expect(function() {
                        i18n.loadFromDir(value);
                    }).to.throwError(function(e) {
                        expect(e.message).to.be('Provide a path to a directory with localization files');
                    });
                });
            }
        );

        it('should throw if keysets are not set', function() {
            i18n.reset();
            i18n.setAllowedLangs(['ru']);

            expect(function() {
                i18n.loadFromDir(__dirname + '/localizations');
            }).to.throwError(function(e) {
                expect(e.message).to.be(
                    'Before loading, please define keysets to look for using i18n.setKeysets([...])'
                );
            });
        });

        it('should throw if allowed langs were net specified', function() {
            i18n.reset();
            i18n.setKeysets(['smth']);

            expect(function() {
                i18n.loadFromDir(__dirname + '/localizations');
            }).to.throwError(function(e) {
                expect(e.message).to.be(
                    'Before loading, please define allowed langs using i18n.setAllowedLangs([...])'
                );
            });
        });

        it('should return i18n for chaining', function() {
            expect(i18n.loadFromDir(__dirname + '/localizations')).to.be(i18n);
        });
    });

    describe('isConfigured', function() {
        it('should return true when keysets and allowedLangs are set and translations are loaded', function() {
            i18n.setAllowedLangs(['ru']);
            i18n.setKeysets(['another', 'keyset']);
            i18n.loadFromDir(__dirname + '/localizations');

            expect(i18n.isConfigured()).to.be(true);
        });

        it('should return false if no translations were loaded', function() {
            i18n.setAllowedLangs(['ru']);
            i18n.setKeysets(['another', 'keyset']);

            expect(i18n.isConfigured()).to.be(false);
        });
    });
});
