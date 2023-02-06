var module = require('../libs/set_mobile_version');
var nullLogger = require('log4js').getLogger();

describe('Set Mobile Version', function() {
    before(function() {
        this._finish = function() {};
    });
    describe('без настройки', function() {
        beforeEach(function() {
            this._redir = '';
            this._req = {
                _parsedUrl: {
                    pathname: '/'
                },
                uatraits: {},
                logger: nullLogger
            };
            this._res = {
                redirect: (status, url) => {
                    this._redir = status + ':' + url;
                }
            };
        });
        it('правильно обрабатывает мобильные', function() {
            this._req.uatraits.isMobile = true;
            module(this._req, this._res, this._finish);
            this._req.isMobile.should.equal(true);
            //this._redir.should.not.equal('');
        });
        it('правильно обрабатывает десктопы', function() {
            module(this._req, this._res, this._finish);
            should.not.exist(this._req.isMobile);
            //this._redir.should.equal('');
        });
        it('правильно обрабатывает планшеты', function() {
            this._req.uatraits.isMobile = true;
            this._req.uatraits.isTablet = true;
            module(this._req, this._res, this._finish);
            should.not.exist(this._req.isMobile);
            //this._redir.should.equal('');
        });
        it('правильно обрабатывает неизвестные устпойства', function() {
            this._req.uatraits = undefined;
            module(this._req, this._res, this._finish);
            should.not.exist(this._req.isMobile);
            //this._redir.should.equal('');
        });
    });
    
    describe('приоритет мобильных', function() {
        beforeEach(function() {
            this._redir = '';
            this._req = {
                _parsedUrl: {
                    pathname: '/'
                },
                mycookie: {
                    '44': [0]
                },
                uatraits: {
                },
                logger: nullLogger
            };
            this._res = {
                redirect: (status, url) => {
                    this._redir = status + ':' + url;
                }
            };
        });
        it('правильно обрабатывает мобильные', function() {
            this._req.uatraits.isMobile = true;
            module(this._req, this._res, this._finish);
            this._req.isMobile.should.equal(true);
            //this._redir.should.not.equal('');
        });
        it('правильно обрабатывает десктопы', function() {
            module(this._req, this._res, this._finish);
            this._req.isMobile.should.equal(true);
            //this._redir.should.not.equal('');
        });
        it('правильно обрабатывает планшеты', function() {
            this._req.uatraits.isMobile = true;
            this._req.uatraits.isTablet = true;
            module(this._req, this._res, this._finish);
            this._req.isMobile.should.equal(true);
            //this._redir.should.not.equal('');
        });
        it('правильно обрабатывает неизвестные устпойства', function() {
            this._req.uatraits = undefined;
            module(this._req, this._res, this._finish);
            this._req.isMobile.should.equal(true);
            //this._redir.should.not.equal('');
        });
    });
    
    describe('приоритет десктопных', function() {
        beforeEach(function() {
            this._redir = '';
            this._req = {
                _parsedUrl: {
                    pathname: '/'
                },
                mycookie: {
                    '44': [1]
                },
                uatraits: {
                },
                logger: nullLogger
            };
            this._res = {
                redirect: (status, url) => {
                    this._redir = status + ':' + url;
                }
            };
        });
        it('правильно обрабатывает мобильные', function() {
            this._req.uatraits.isMobile = true;
            module(this._req, this._res, this._finish);
            should.not.exist(this._req.isMobile);
            //this._redir.should.equal('');
        });
        it('правильно обрабатывает десктопы', function() {
            module(this._req, this._res, this._finish);
            should.not.exist(this._req.isMobile);
            //this._redir.should.equal('');
        });
        it('правильно обрабатывает планшеты', function() {
            this._req.uatraits.isMobile = true;
            this._req.uatraits.isTablet = true;
            module(this._req, this._res, this._finish);
            should.not.exist(this._req.isMobile);
            //this._redir.should.equal('');
        });
        it('правильно обрабатывает неизвестные устпойства', function() {
            this._req.uatraits = undefined;
            module(this._req, this._res, this._finish);
            should.not.exist(this._req.isMobile);
            //this._redir.should.equal('');
        });
    });
    
    describe.skip('редиректы', function() {
        beforeEach(function() {
            this._redir = '';
            this._req = {
                mordazone: 'tld',
                _parsedUrl: {
                    pathname: '/'
                },
                mycookie: {
                    '44': [0]
                },
                uatraits: {
                },
                logger: nullLogger
            };
            this._res = {
                redirect: (status, url) => {
                    this._redir = status + ':' + url;
                }
            };
        });
        
        it('с корня', function() {
            module(this._req, this._res, this._finish);
            this._redir.should.equal('302:https://m.tune.yandex.tld/region');

            this._req._parsedUrl.pathname = '/tune';
            module(this._req, this._res, this._finish);
            this._redir.should.equal('302:https://m.tune.yandex.tld/region');
            
            this._req._parsedUrl.pathname = '/tune/';
            module(this._req, this._res, this._finish);
            this._redir.should.equal('302:https://m.tune.yandex.tld/region');
        });
        it('с geo', function() {
            this._req._parsedUrl.pathname = '/geo';
            module(this._req, this._res, this._finish);
            this._redir.should.equal('302:https://m.tune.yandex.tld/region');
            
            this._req._parsedUrl.pathname = '/geo/';
            module(this._req, this._res, this._finish);
            this._redir.should.equal('302:https://m.tune.yandex.tld/region');

            this._req._parsedUrl.pathname = '/tune/geo';
            module(this._req, this._res, this._finish);
            this._redir.should.equal('302:https://m.tune.yandex.tld/region');
            
            this._req._parsedUrl.pathname = '/tune/geo/';
            module(this._req, this._res, this._finish);
            this._redir.should.equal('302:https://m.tune.yandex.tld/region');
        });
        it('с lang', function() {
            this._req._parsedUrl.pathname = '/lang';
            module(this._req, this._res, this._finish);
            this._redir.should.equal('302:https://m.tune.yandex.tld/lang');
            
            this._req._parsedUrl.pathname = '/lang/';
            module(this._req, this._res, this._finish);
            this._redir.should.equal('302:https://m.tune.yandex.tld/lang');
            
            this._req._parsedUrl.pathname = '/tune/lang';
            module(this._req, this._res, this._finish);
            this._redir.should.equal('302:https://m.tune.yandex.tld/lang');
            
            this._req._parsedUrl.pathname = '/tune/lang/';
            module(this._req, this._res, this._finish);
            this._redir.should.equal('302:https://m.tune.yandex.tld/lang');
        });
        it('с других страниц', function() {
            ['/adv', '/search', '/redirect'].forEach(page => {
                this._redir = '';
                this._req._parsedUrl.pathname = page;
                module(this._req, this._res, this._finish);
                this._redir.should.equal('302:https://m.tune.yandex.tld/');
                
                this._redir = '';
                this._req._parsedUrl.pathname = page + '/';
                module(this._req, this._res, this._finish);
                this._redir.should.equal('302:https://m.tune.yandex.tld/');
                
                this._redir = '';
                this._req._parsedUrl.pathname = '/tune/' + page + '/';
                module(this._req, this._res, this._finish);
                this._redir.should.equal('302:https://m.tune.yandex.tld/');
            });
        });
    });
    
});