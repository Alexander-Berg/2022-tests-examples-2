const webpackRunner = require('../webpack-runner'),
    evalBundle = require('../eval-bundle'),
    conf = require('./config.js');

describe('[webpack] Сборка страничных клиентсайд бандлов', function () {
    let assets;

    this.timeout(30000);

    before(function () {
        return webpackRunner(conf).then(res => {
            assets = res.assets;
        });
    });

    describe('бандлы собираются', function () {
        it('для single-entry', function () {
            assets.should.be.an('object')
                .and.include.keys(['main.css', 'main.js']);
        });

        it('для multi-entry', function () {
            assets.should.be.an('object')
                .and.include.keys([
                    'one.css',
                    'one.js',
                    'two.css',
                    'two.js',
                    'three.css',
                    'three.js',
                    'four.css',
                    'four.js',
                    'five.css',
                    'five.js'
                ]);
        });
    });

    describe('содержимое бандлов', function () {
        const fs = require('fs'),
            util = require('util'),
            path = require('path');
        let oneJs, oneCss,
            twoJs, twoCss,
            threeJs, threeCss,
            fourJs, fourCss;

        function contentFor(entry) {
            let js = assets[`${entry}.js`],
                css = assets[`${entry}.css`];

            let jsPromise, cssPromise;

            if (!js) {
                jsPromise = Promise.resolve([]);
            } else {
                js = path.resolve(__dirname, js);
                jsPromise = evalBundle(entry, js).then(res => {
                    return res.logged;
                });
            }

            if (!css) {
                cssPromise = Promise.resolve('');
            } else {
                css = path.resolve(__dirname, css);
                cssPromise = util.promisify(fs.readFile)(css, 'utf-8');
            }

            return Promise.all([
                jsPromise,
                cssPromise
            ]);
        }
        before(function () {
            return Promise.all([
                contentFor('one').then(([js, css]) => {
                    oneJs = js;
                    oneCss = css;
                }),
                contentFor('two').then(([js, css]) => {
                    twoJs = js;
                    twoCss = css;
                }),
                contentFor('three').then(([js, css]) => {
                    threeJs = js;
                    threeCss = css;
                }),
                contentFor('four').then(([js, css]) => {
                    fourJs = js;
                    fourCss = css;
                })
            ]);
        });

        describe('одинаковые бандлы равны', function () {
            it('js бандлы 1 и 3', function () {
                threeJs.should.deep.equal(oneJs);
            });

            it('css бандлы 1 и 3', function () {
                threeCss.should.equal(oneCss);
            });

            it('js бандлы 2 и 4', function () {
                fourJs.should.deep.equal(twoJs);
            });

            it('css бандлы 2 и 4', function () {
                fourCss.should.equal(twoCss);
            });
        });

        describe('js бандл содержит', function () {
            it('серверсайд шаблоны, импортированных из точки входа', function () {
                oneJs.should.contain('SERVER:imported');
                oneJs.should.contain('SERVER:imported-no-client');
            });

            it('серверсайд шаблоны, импортированных из импортированного модуля', function () {
                oneJs.should.contain('SERVER:next-imported');
                oneJs.should.contain('SERVER:no-client');
            });

            it('серверсайд шаблоны, используемых в серверсайд модуле, импортированном на клиентсайд', function () {
                oneJs.should.contain('SERVER:next-imported');
                oneJs.should.contain('SERVER:imported-has-client');
                oneJs.should.not.contain('SERVER:not-imported');
            });

            it('кода из точки входа', function () {
                oneJs.should.not.contain('SERVER:entry');
            });

            it('зависимость серверсайд шаблона из модуля, импортированного клиентсайд кодом', function () {
                oneJs.should.not.contain('SERVER:nested-dep');
            });
        });

        describe('js бандл содержит', function () {
            it('импортированный из модуля', function () {
                oneJs.should.contain('CLIENT:imported');
            });

            it('импортированный из модуля, импортированного другим модулем', function () {
                oneJs.should.contain('CLIENT:next-imported');
                oneJs.should.contain('CLIENT:imported-has-client');
            });

            it('импортированный клиентсайд модулем', function () {
                oneJs.should.contain('CLIENT:client-imported');
            });

            it('импортированный клиентсайд модулем шаблон', function () {
                oneJs.should.contain('SERVER:client-imported');
                oneJs.should.contain('SERVER:imported-to-clientside');
            });

            it('зависимость импортированного клиентсайд модулем шаблона', function () {
                oneJs.should.contain('SERVER:imported-dep');
            });
        });

        describe('css бандл содержит стили', function () {
            it('импортированные из серверсайд модуля', function () {
                oneCss.should.contain('STYLE:style-in-server');
            });

            it('импортированные из клиентсайд модуля', function () {
                oneCss.should.contain('STYLE:style-in-client');
            });
        });

        describe('js бандл соседнего entry содержит', function () {
            it('клиентсайд модуль, используемый в первом энтри', function () {
                twoJs.should.contain('CLIENT:imported');
            });
        });
    });
});
