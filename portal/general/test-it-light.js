const path = require('path'),
    runner = require('../lib/testrunner.js'),
    clearColors = require('../lib/clear-colors');

module.exports = require('enb/lib/build-flow').create()
    .name('test-it-light')
    .target('target', '?.test.log')
    .useSourceFilename('sourceTarget')
    .defineOption('prepend', [])
    .defineOption('reporter')
    .defineOption('copy')
    .defineOption('failOnError')
    .defineOption('inBrowser')
    .defineOption('exclude')
    .defineOption('jQuery')
    .needRebuild(function(cache) {
        /* Эта функция нужна только для того, чтобы форсировать пересборку
         * тестов, если прошлый прогон был неуспешен (и опция failOnError отключена).
         * Проверка свежести исходников происходит внутри build-flow сразу после выполнения
         * этой функции.
         */
        return !cache.get('passed');
    })
    .builder(function() {
        let target = this.node.resolvePath(path.basename(this._target)),
            source = this.node.resolvePath(this._sourceTarget),
            self = this,
            cache = self.node.getNodeCache(this._target),
            logger = this.node.getLogger(),
            prepend = this._prepend,
            reporter = this._reporter,
            copy = this._copy,
            inBrowser = this._inBrowser,
            jQuery = this._jQuery,
            success = true;

        return runner({
            target: target,
            files: prepend.concat(source),
            base: self.node.getRootDir(),
            reporter: reporter,
            browser: inBrowser,
            jQuery: jQuery
        }).then((data) => {
            logger.logAction('test-it-light', self._target,
                data.tests + ' test' + (data.tests !== 1 ? 's' : '') + ' passed in ' + data.time + 's');
            return data.output;
        }, (e) => {
            success = false;
            logger.logErrorAction('test-it-light', self._target, 'Error while running Karma:');
            console.error(e.output, e.msg);
        }).then(function (output) {
            let str = 'Tests for ' + target + (success ? ' passed' : ' failed');

            if (copy && output) {
                console.log(output);
            }

            if (self._failOnError && !success) {
                throw new Error(str);
            } else {
                cache.set('passed', success);
            }

            return clearColors(output);
        });
    })
    .createTech();
