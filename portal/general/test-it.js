const path = require('path'),
    runner = require('../lib/testrunner.js'),
    clearColors = require('../lib/clear-colors');

module.exports = require('enb/lib/build-flow').create()
    .name('test-it')
    .target('target', '?.test.log')
    .defineOption('prepend', [])
    .defineOption('reporter')
    .defineOption('copy')
    .defineOption('failOnError')
    .defineRequiredOption('sourceSuffixes')
    .useSourceResult('dirsTarget', '?.levels')
    .useFileList('view.js')
    .needRebuild(function(cache) {
        /* Эта функция нужна только для того, чтобы форсировать пересборку
         * тестов, если прошлый прогон был неуспешен (и опция failOnError отключена).
         * Проверка свежести исходников происходит внутри build-flow сразу после выполнения
         * этой функции.
         */
        return !cache.get('passed');
    })
    .builder(function(levels, sources) {
        let target = this.node.resolvePath(path.basename(this._target)),
            self = this,
            cache = self.node.getNodeCache(this._target),
            logger = this.node.getLogger(),
            prepend = this._prepend,
            reporter = this._reporter,
            copy = this._copy,
            testSuffix = this._sourceSuffixes[this._sourceSuffixes.length - 1],
            sourcesByLevel = this._getTestLevels(levels.items, sources, testSuffix),
            success = true;

        return sourcesByLevel.reduce(function(current, next) {
            return current.then(function(output) {
                return runner({
                    target: target,
                    level: next.level,
                    files: prepend.concat(next.sources),
                    base: self.node.getRootDir(),
                    reporter: reporter
                }).then(function(data) {
                    logger.logAction('test-it', self._target,
                        data.tests + ' test' + (data.tests !== 1 ? 's' : '') + ' passed in ' + data.time + 's');
                    return output + data.output;
                }, function (data) {
                    success = false;
                    logger.logErrorAction('test-it', self._target, 'Error while running Mocha:');
                    console.error(`${output}\n${data.output}`);
                    logger.logErrorAction('test-it', self._target, data.msg);
                    return output + data.output;
                });
            });
        }, Promise.resolve('')).then(function (output) {
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
    }).methods({
        /**
         * Формирование наборов исходников с тестами по уровням.
         * Возвращает только такие наборы, в которых есть тесты.
         * @param {Array} levels список всех уровней
         * @param {FileList} sources список всех исходников и тестов
         * @param {String} testSuffix суффикс файлов тестов
         * @returns {Array}
         */
        _getTestLevels: function(levels, sources, testSuffix) {
            var levelSources = [],
                sourcesByLevel = [];

            for (var i = 0; i < levels.length; i++) {
                var level = levels[i]._path + '/',
                    levelTests = [];

                sources.forEach(function(source) {
                    var isCurrentLevel = source.fullname.indexOf(level) === 0;
                    if (isCurrentLevel) {
                        if (source.suffix === testSuffix) {
                            levelTests.push(source.fullname);
                        } else {
                            levelSources.push(source.fullname);
                        }
                    }
                    return isCurrentLevel;
                });

                if (levelTests.length) {
                    sourcesByLevel.push({
                        level: level,
                        sources: levelSources.concat(levelTests)
                    });
                }
            }
            return sourcesByLevel;
        }
    })
    .createTech();
