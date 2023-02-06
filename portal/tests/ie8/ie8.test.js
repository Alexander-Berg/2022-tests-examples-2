const vm = require('vm');
const fs = require('fs');

const webpackRunner = require('../webpack-runner.js');
const conf = require('./config.js')();

describe('[webpack] IE8TemplatePlugin5', function () {
    this.timeout(30000);

    // let stats, warnings;
    before(function () {
        return webpackRunner(conf)/*.then(([res, wr]) => {
            stats = res;
            warnings = wr;
        })*/;
    });

    let bundle;

    describe('бандлы выполняются', function () {
        beforeEach(function () {
            const filename = __dirname + '/client-side/bundles/main.js';
            const contents = fs.readFileSync(filename, 'utf-8');
            let module = {};
            vm.runInNewContext(contents, {
                module
            }, {
                filename
            });
            bundle = module.exports;
        });

        it('возвращает корректные значения', function () {
            bundle.runFuncExport().should.equal(`func result abc`);
            bundle.runVarExport().should.equal(`var result abc2`);
            bundle.instantRunResult().should.equal(`func result abc\nvar result abc2`);
        });
    });
});
