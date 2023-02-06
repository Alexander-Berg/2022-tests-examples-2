const webpackRunner = require('../webpack-runner'),
    conf = require('./config.js'),
    {readFileSync} = require('fs'),
    chaiJestSnapshot = require('chai-jest-snapshot');

beforeEach(function() {
    chaiJestSnapshot.configureUsingMochaContext(this);
});

describe('[webpack] Инлайн ресурсов', function () {
    describe('серверсайд бандл', function() {
        let assets,
            bundle;
        before(function () {
            this.timeout(10000);
            chaiJestSnapshot.resetSnapshotRegistry();

            return webpackRunner(conf)
                .then(res => {
                    assets = res.assets;
                    assets.should.be.an('object')
                        .and.have.property('test.js');
                    bundle = require(assets['test.js']);
                });

        });
        describe('стили', function () {
            it('генерирует css бандл с extracted стилями', function () {
                assets.should.have.property('test.css');
                const css = readFileSync(assets['test.css'], 'utf-8');
                css.should.matchSnapshot();
            });

            it('инлайнит', function () {
                const style = bundle.style;
                style.should.be.an('object');
                const inline = style.inline;
                inline.should.be.an('array');
                inline[0].toString().should.matchSnapshot('styl?inline');
                inline[1].toString().should.matchSnapshot('css?inline');
                inline.should.have.lengthOf(2);
            });

            it('проставляет ссылки', function () {
                const style = bundle.style;
                style.should.be.an('object');
                const link = style.link;
                link.should.be.an('array');
                link[0].toString().should.matchSnapshot('styl?link');
                link[1].toString().should.matchSnapshot('css?link');
                link.should.have.lengthOf(2);
            });
        });

        describe('скрипты', function () {
            it('инлайнит', function () {
                const scripts = bundle.scripts;
                scripts.should.be.an('object');
                const inline = scripts.inline;
                inline.should.be.an('array');
                inline[0].toString().should.matchSnapshot();
                inline.should.have.lengthOf(1);
            });

            it('проставляет ссылки', function () {
                const scripts = bundle.scripts;
                scripts.should.be.an('object');
                const link = scripts.link;
                link.should.be.an('array');
                link[0].toString().should.matchSnapshot();
                link.should.have.lengthOf(1);
            });

            it('вырезает из бандла', function () {
                const scripts = bundle.scripts;
                scripts.should.be.an('object');
                const extracted = scripts.extracted;
                extracted.should.be.an('array');
                extracted[0].should.matchSnapshot();
                extracted.should.have.lengthOf(1);
            });

            it('импортирует', function () {
                const scripts = bundle.scripts;
                scripts.should.be.an('object');
                const imported = scripts.imported;
                imported.should.be.an('array');
                imported[0].should.matchSnapshot();
                imported.should.have.lengthOf(1);
            });
        });

        describe('картинки', function () {
            it('инлайнит', function () {
                const images = bundle.images;
                images.should.be.an('object');
                const inline = images.inline;
                inline.should.be.an('array');
                inline[0].toString().should.matchSnapshot('svg?inline');
                inline.should.have.lengthOf(1);
            });

            it('энкодит', function () {
                const images = bundle.images;
                images.should.be.an('object');
                const encode = images.encode;
                encode.should.be.an('array');
                encode[0].toString().should.matchSnapshot('svg?encode');
                encode[1].toString().should.matchSnapshot('png?encode');
                encode.should.have.lengthOf(2);
            });

            it('проставляет ссылки', function () {
                const images = bundle.images;
                images.should.be.an('object');
                const link = images.link;
                link.should.be.an('array');
                link[0].toString().should.matchSnapshot('svg?link');
                link[1].toString().should.matchSnapshot('png?link');
                link.should.have.lengthOf(2);
            });

            it('проставляет ссылки2', function () {
                const images = bundle.images;
                images.should.be.an('object');
                const link = images.link2;
                link.should.be.an('array');
                link[0].toString().should.matchSnapshot('svg');
                link[1].toString().should.matchSnapshot('png');
                link.should.have.lengthOf(2);
            });
        });
    });
});
