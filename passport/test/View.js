var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');

var View = require('../View');

describe('View', function() {
    beforeEach(function() {
        this.renderer = sinon.stub();
        this.templatesDir = __dirname + '/templatesDir';
        this.filename = 'testTemplate.js';
        this.fileBasename = 'testTemplate';
        this.data = {a: 'bc'};
    });

    describe('Static setRenderer', function() {
        it('should throw if the argument is not a function', function() {
            expect(function() {
                View.setRenderer('nope');
            }).to.throwError(function(err) {
                expect(err.message).to.be(
                    'Renderer should be a function accepting templatesDir path, filename and templating data'
                );
            });
        });

        it('should return the view for chaining', function() {
            expect(View.setRenderer(this.renderer)).to.be(View);
        });
    });

    describe('Static setTemplatesDir', function() {
        it('should throw if called with anything but a string', function() {
            expect(function() {
                View.setTemplatesDir(123);
            }).to.throwError(function(err) {
                expect(err.message).to.be('Templates dir is expected to be a path to templates directory');
            });
        });

        it('should return the view for chaining', function() {
            expect(View.setTemplatesDir(this.templatesDir)).to.be(View);
        });
    });

    describe('Static yateRenderer', function() {
        it('should throw if templatesDirPath is not a string', function() {
            var that = this;

            expect(function() {
                View.yateRenderer(true, that.filename, that.data);
            }).to.throwError(function(err) {
                expect(err.message).to.be('Templates dir is expected to be a path to templates directory');
            });
        });

        it('should throw if templatesDirPath is /', function() {
            var that = this;

            expect(function() {
                View.yateRenderer('/', that.filename, that.data);
            }).to.throwError(function(err) {
                expect(err.message).to.be('Templates dir is expected to be a path to templates directory');
            });
        });

        it('should throw if filename is not a string', function() {
            var that = this;

            expect(function() {
                View.yateRenderer(that.templatesDir, 123, that.data);
            }).to.throwError(function(err) {
                expect(err.message).to.be('Filename should be a name of the template file');
            });
        });

        it('should throw if filename does not ends in .js', function() {
            var that = this;

            expect(function() {
                View.yateRenderer(that.templatesDir, 'nopenope', that.data);
            }).to.throwError(function(err) {
                expect(err.message).to.be('Filename should be a name of the template file');
            });
        });

        it('should throw if data is not a plain object', function() {
            var that = this;

            expect(function() {
                View.yateRenderer(that.templatesDir, that.filename, new Function());
            }).to.throwError(function(err) {
                expect(err.message).to.be('Templating data should be a plain object');
            });
        });

        it('should call yate.run with the filename without extension and the given data object', function() {
            sinon.stub(require('yate/lib/runtime'), 'run');

            View.yateRenderer(this.templatesDir, this.filename, this.data);
            expect(require('yate/lib/runtime').run.calledOnce).to.be(true);
            expect(require('yate/lib/runtime').run.calledWithExactly(this.fileBasename, this.data)).to.be(true);

            require('yate/lib/runtime').run.restore();
        });
    });

    describe('render', function() {
        beforeEach(function() {
            View.setRenderer(this.renderer).setTemplatesDir(this.templatesDir);

            var ViewSuccessor = require('inherit')(View, {
                name: 'TstView'
            });

            this.view = new ViewSuccessor();

            sinon.stub(this.view, 'getTemplate').returns(this.filename);
            sinon.stub(this.view, 'compile').returns(when.resolve(this.data));

            this.arg1 = {};
            this.arg2 = {};

            this.rendered = this.view.render(this.arg1, this.arg2);
        });
        afterEach(function() {
            View.reset();
        });

        it('should throw if renderer is not set up', function() {
            View.reset();
            View.setTemplatesDir(this.templatesDir);

            var that = this;

            expect(function() {
                that.view.render();
            }).to.throwError(function(err) {
                expect(err.message).to.be('Renderer should be defined with View.setRenderer method');
            });
        });

        it('should throw if templatesDir is not set up', function() {
            View.reset();
            View.setRenderer(this.renderer);

            var that = this;

            expect(function() {
                that.view.render();
            }).to.throwError(function(err) {
                expect(err.message).to.be('Templates dir path should be defined with View.setTemplatesDir');
            });
        });

        it('should call the renderer set up through View.setRenderer', function(done) {
            var that = this;

            this.rendered
                .then(function() {
                    expect(that.renderer.calledOnce).to.be(true);
                    done();
                })
                .then(null, done);
        });

        it('should pass the templatesDir set up through View.setTemplatesDir to the renderer', function(done) {
            var that = this;

            this.rendered
                .then(function() {
                    expect(that.renderer.calledWith(that.templatesDir)).to.be(true);
                    done();
                })
                .then(null, done);
        });

        it('should pass the result of this.getTemplate as a template filename', function(done) {
            var that = this;

            this.rendered
                .then(function() {
                    expect(that.renderer.firstCall.args[1]).to.be(that.filename);
                    done();
                })
                .then(null, done);
        });

        it('should pass the result of this.compile as template data', function(done) {
            var that = this;

            this.rendered
                .then(function() {
                    expect(that.renderer.firstCall.args[2]).to.be(that.data);
                    done();
                })
                .then(null, done);
        });

        it('should pass the arguments to compile method', function() {
            expect(this.view.compile.calledWithExactly(this.arg1, this.arg2)).to.be(true);
        });
    });
});
