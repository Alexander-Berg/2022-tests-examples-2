describe('home.resources', function() {
    before(function() {
        this._oldGetFromCache = home.getFromCache;
        home.getFromCache = function(path) {
            return '<content of ' + path + '>';
        };
    });
    after(function() {
        home.getFromCache = this._oldGetFromCache;
    });
    
    describe('add', function() {
        beforeEach(function() {
            this.resources = new home.Resources('test', {}, function(name, data) {
                return JSON.stringify({view: name, data: data});
            });
        });

        it('добавляет ресурс в дефолтное место', function() {
            this.resources.add('path/to/resource.js', 'js');
            this.resources.add('path/to/resource.css', 'css');
            
            this.resources._content.should.deep.equal({
                head: {
                    css: [
                        {
                            resource: 'path/to/resource.css',
                            kind: 'css',
                            inline: undefined
                        }
                    ],
                    js: []
                },
                'head-end': {
                    css: [],
                    js: []
                },
                body: {
                    css: [],
                    js: []
                },
                'ready-scripts': {
                    css: [],
                    js: [
                        {
                            resource: 'path/to/resource.js',
                            kind: 'js',
                            inline: undefined
                        }
                    ]
                }
            });
        });
        
        it('добавляет ресурс в указанное место', function() {
            this.resources.add('path/to/resource.js', 'js', 'head');
            this.resources.add('path/to/resource.css', 'css', 'body');
            
            this.resources._content.should.deep.equal({
                head: {
                    css: [],
                    js: [{
                        resource: 'path/to/resource.js',
                        kind: 'js',
                        inline: undefined
                    }]
                },
                'head-end': {
                    css: [],
                    js: []
                },
                body: {
                    css: [{
                        resource: 'path/to/resource.css',
                        kind: 'css',
                        inline: undefined
                    }],
                    js: []
                },
                'ready-scripts': {
                    css: [],
                    js: []
                }
            });
        });
        
        it('добавляет инлайн ресурс в указанное место', function() {
            this.resources.add('blabla()', 'js', 'head', true);
            this.resources.add('blabla{}', 'css', false, true);
            
            this.resources._content.should.deep.equal({
                head: {
                    css: [{
                        resource: 'blabla{}',
                        kind: 'css',
                        inline: true
                    }],
                    js: [{
                        resource: 'blabla()',
                        kind: 'js',
                        inline: true
                    }]
                },
                'head-end': {
                    css: [],
                    js: []
                },
                body: {
                    css: [],
                    js: []
                },
                'ready-scripts': {
                    css: [],
                    js: []
                }
            });
        });
        
        it('кидает исключение, если указан неправильный тип', function() {
            var self = this,
                f = function() {
                    self.resources.add('/path/to/resource.js', 'teapot');
                };
            f.should.throw(TypeError, 'Don\'t know where to place "teapot" and no default was found');
        });
        
        it('кидает исключение, если указан неправильный тип для выбранного места', function() {
            var self = this,
                f = function() {
                    self.resources.add('/path/to/resource.js', 'teapot', 'head');
                };
            f.should.throw(TypeError, 'Don\'t know how to place "teapot" into "head"');
        });
        
        it('кидает исключение, если указано неправильное место', function() {
            var self = this,
                f = function() {
                    self.resources.add('/path/to/resource.js', 'js', 'somewhere');
                };
            f.should.throw(RangeError, 'Invalid place "somewhere"');
        });
        
        it('кидает исключение, если указанное место уже размещено', function() {
            var self = this,
                f = function() {
                    self.resources.add('/path/to/resource.js', 'js', 'head');
                    self.resources.getHTML('head');
                    self.resources.add('/path/too/late.js', 'js', 'head');
                };
            f.should.throw('Already placed "head"');
        });
    });
    
    describe('inline', function() {
        beforeEach(function() {
            this.resources = new home.Resources('test', {}, function(name, data) {
                return JSON.stringify({view: name, data: data});
            });
        });
        
        it('добавляет инлайн ресурс в дефолтное место', function() {
            this.resources.inline('path/to/resource.js', 'js');
            this.resources.inline('path/to/resource.css', 'css');
            
            this.resources._content.should.deep.equal({
                head: {
                    css: [{
                        resource: '<content of path/to/resource.css>',
                        kind: 'css',
                        inline: true
                    }],
                    js: []
                },
                'head-end': {
                    css: [],
                    js: []
                },
                body: {
                    css: [],
                    js: []
                },
                'ready-scripts': {
                    css: [],
                    js: [{
                        resource: '<content of path/to/resource.js>',
                        kind: 'js',
                        inline: true
                    }]
                }
            });
        });
        
        it('добавляет инлайн ресурс в указанное место', function() {
            this.resources.inline('path/to/resource.js', 'js', 'body');
            this.resources.inline('path/to/resource.css', 'css', 'body');
            
            this.resources._content.should.deep.equal({
                head: {
                    css: [],
                    js: []
                },
                'head-end': {
                    css: [],
                    js: []
                },
                body: {
                    css: [{
                        resource: '<content of path/to/resource.css>',
                        kind: 'css',
                        inline: true
                    }],
                    js: [{
                        resource: '<content of path/to/resource.js>',
                        kind: 'js',
                        inline: true
                    }]
                },
                'ready-scripts': {
                    css: [],
                    js: []
                }
            });
        });
    });
    
    describe('getHTML', function() {
        beforeEach(function() {
            this.resources = new home.Resources('test', {}, function(name, data) {
                return JSON.stringify({view: name, data: data});
            });
        });
        it('кидает исключение при попытке взять несуществующую группу', function() {
            var resources = this.resources,
                f = function() {
                    resources.getHTML('bla');
                };
            f.should.throw('Resources: unknown placement! bla');
        });
        
        it('возвращает HTML для одного ресурса', function() {
            this.resources.add('path/to/resource.js', 'js');
            this.resources.getHTML('ready-scripts').should.equal('{"view":"script-src","data":{"url":"//yastatic.net/frozen/1.235/path/to/resource.js"}}');
        });
        it('возвращает HTML для одного инлайн ресурса', function() {
            this.resources.add('bla()', 'js', false, true);
            this.resources.getHTML('ready-scripts').should.equal('{"view":"script","data":{"content":"bla()"}}');
        });
        it('возвращает HTML для чередования инлайн и ссылок', function() {
            this.resources.add('path/to/1.js', 'js');
            this.resources.inline('path/to/2.js', 'js');
            this.resources.add('path/to/3.js', 'js');
            this.resources.add('bla4()', 'js', false, true);
            this.resources.getHTML('ready-scripts')
                .should.equal('{"view":"script-src","data":{"url":"//yastatic.net/frozen/1.235/path/to/1.js"}}' +
                    '{"view":"script","data":{"content":"<content of path/to/2.js>"}}' +
                    '{"view":"script-src","data":{"url":"//yastatic.net/frozen/1.235/path/to/3.js"}}' +
                    '{"view":"script","data":{"content":"bla4()"}}');
        });
        it('группирует одинаковые типы инлайна, следующие подряд', function() {
            this.resources.add('path/to/1.js', 'js');
            this.resources.inline('path/to/2.js', 'js');
            this.resources.add('bla3()', 'js', false, true);
            this.resources.inline('path/to/4.js', 'js');
            this.resources.inline('path/to/5.css', 'css', 'ready-scripts');
            this.resources.add('path/to/6.js', 'js');
            this.resources.add('path/to/7.js', 'js');
            this.resources.getHTML('ready-scripts')
                .should.equal('{"view":"style","data":{"content":"<content of path/to/5.css>"}}' +
                    '{"view":"script-src","data":{"url":"//yastatic.net/frozen/1.235/path/to/1.js"}}' +
                    '{"view":"script","data":{"content":"<content of path/to/2.js>bla3()<content of path/to/4.js>"}}' +
                    '{"view":"script-src","data":{"url":"//yastatic.net/frozen/1.235/path/to/6.js"}}' +
                    '{"view":"script-src","data":{"url":"//yastatic.net/frozen/1.235/path/to/7.js"}}');
        });

        describe('использует nonce', function() {
            beforeEach(function() {
                this.resources = new home.Resources('test', {nonce: 'test-nonce'}, function(name, data) {
                    return JSON.stringify({view: name, data: data});
                });
            });
            
            it('для css', function() {
                this.resources.add('path/to/1.css', 'css');
                this.resources.inline('path/to/2.css', 'css');

                this.resources.getHTML('head')
                    .should.equal('{"view":"link-href","data":{"url":"//yastatic.net/frozen/1.235/path/to/1.css"}}' +
                    '{"view":"style","data":{"content":"<content of path/to/2.css>","nonce":"test-nonce"}}');
            });

            it('для js', function() {
                this.resources.add('path/to/1.js', 'js');
                this.resources.inline('path/to/2.js', 'js');

                this.resources.getHTML('ready-scripts')
                    .should.equal('{"view":"script-src","data":{"url":"//yastatic.net/frozen/1.235/path/to/1.js"}}' +
                    '{"view":"script","data":{"content":"<content of path/to/2.js>","nonce":"test-nonce"}}');
            });
        });
    });
});