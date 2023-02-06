const webpackRunner = require('../webpack-runner.js');
const initConf = require('./config.js');
const { matchObject } = require('webpack/lib/ModuleFilenameHelpers');

const translations = ['ru', 'en'].reduce((mem, lang) => {
    const LANG = lang.toUpperCase();
    return {
        ...mem,
        [lang]: {
            async: `async${LANG}`,
            nested: {
                test: `nestedTest${LANG}`,
                defaultExportVariable: `nestedDefaultExportVariable${LANG}`,
                singleExportVariable: `nestedSingleExportVariable${LANG}`,
            },
            test: `test${LANG}`,
            variable: `variable${LANG}`,
            notExportedVariable: `notExportedVariable${LANG}`,
            eval: {
                test: `evalTest${LANG}`,
                another: `evalAnother${LANG}`,
            },
            defaultExportVariable: `defaultExportVariable${LANG}`,
            singleExportVariable: `singleExportVariable${LANG}`,
            exportAllNested: {
                one: `one${LANG}`,
                another: `another${LANG}`,
            },
            condition: {
                test1: `test1${LANG}`,
                test2: `test2${LANG}`,
                notUsed: `notUsed${LANG}`,
            },
            client: {
                translation: `client${LANG}`,
                direct: `direct${LANG}`,
                variableDirect: `variableDirect${LANG}`,
                evalDirect: {
                    one: `evalDirect${LANG}`,
                },
                try: `try${LANG}`
            },
            array: [`one ${LANG}`, `two ${LANG}`, `more ${LANG}`],
            exportArray: [`export one ${LANG}`, `export two ${LANG}`, `export more ${LANG}`],
            unJoinedArray: [`unjoined one ${LANG}`, `unjoined two ${LANG}`, `unjoined more ${LANG}`],
            nestedDepthTest: {
                one: `nestedDepthTest1${LANG}`,
                two: `nestedDepthTest2${LANG}`
            }
        },
    };
}, {});

function getTranslation(key, locale) {
    const keys = key.split('.');
    let obj = translations[locale];

    for (let i = 0; i < keys.length; ++i) {
        if (obj && obj[keys[i]]) {
            obj = obj[keys[i]];
        } else {
            console.error('home.l10n: undefined translation ' + key);
            return '';
        }
    }

    return obj;
}

function grepModules(objects) {
    let res = [];

    if (!objects) {
        return res;
    }

    for (const item of objects) {
        if (Array.isArray(item.modules)) {
            res.push(...item.modules);
            for (const mod of item.modules) {
                res.push(...grepModules([mod]));
            }
        }
    }

    return res;
}

const conf = initConf(translations);

describe('[webpack] Переводы', function () {
    this.timeout(30000);

    let warnings;
    let json;

    before(function () {
        return webpackRunner(conf).then(res => {
            warnings = res.warnings;
            json = res.json;
        });
    });

    describe('l10n на клиентсайде', function () {
        let req,
            execView,
            bundle;

        beforeEach(function () {
            req = {};
            req.l10n = function () {};
        });

        describe('бандлы собираются', function () {
            let bundleStatRu;
            let bundleStatEn;

            before(function () {
                bundleStatRu = json.children.find(it => /client-side\/ru/.test(it.outputPath));
                bundleStatEn = json.children.find(it => /client-side\/en/.test(it.outputPath));
            });

            it('собирает два чанка', function () {
                const childChunks = bundleStatRu.chunks.filter(ch => ch.children.length > 0);
                childChunks.should.be.an('array')
                    .and.has.lengthOf(1);

                const parentChunks = bundleStatRu.chunks.filter(ch => ch.children.length === 0);
                parentChunks.should.be.an('array')
                    .and.has.lengthOf(1);
            });

            it('файлы с экспортами ключей не входят в сборку', function () {
                const enModules = grepModules(bundleStatEn.chunks);

                enModules.should.be.an('array');

                const exportLangModules = enModules.filter(module => matchObject({
                    test: /\.l10n\.js$/,
                    exclude: /lib\/home\.l10n\.js$/
                }, module.identifier));

                exportLangModules.should.have.lengthOf(0);
            });

            it('warning в сборке с несуществующим ключом', function () {
                const isWarnings = warnings.some((warning) => {
                    return /No translation for subkey/.test(warning.message);
                });

                isWarnings.should.be.equal(true);

                //execView(bundle.localeNotExist).should.contain(`<span class="locale__test"></span>`);
            });
        });

        ['ru', 'en'].forEach(locale => {
            const LANG = locale.toUpperCase();

            describe(locale === 'ru' ? 'основной язык' : 'дополнительный язык', function () {

                beforeEach(function () {
                    bundle = require(`./client-side/${locale}/bundles/client.${locale}.js`);
                    execView = bundle.execView;
                });

                it('переводится по вычисляемому плоскому ключу', function () {
                    execView(bundle.locale).should.contain(`<span class="locale__test">test${LANG}</span>`);
                });

                it('переводится по вычисляемому иерархическому ключу', function () {
                    execView(bundle.localeNested).should.contain(`<span class="locale__test">nestedTest${LANG}</span>`);
                });

                it('переводы работают в динамических импортах', function () {
                    return bundle.loadAsync().then((res) => {
                        execView(res.localeAsync).should.contain(`<span class="locale__test">async${LANG}</span>`);
                    });
                });

                it('переводится по частично вычисляемому ключу без экспорта', function () {
                    execView(bundle.localeEval).should.contain(`<span class="locale__test">evalTest${LANG}</span>`);
                });

                it('не переводится по несуществующему ключу', function () {
                    execView(bundle.localeNotExist).should.contain(`<span class="locale__test"></span>`);
                });

                it('заменяются массивы склонений с числами', function () {
                    execView(bundle.localeArray).should.contain(`<span class="locale__test">one ${LANG}-two ${LANG}-more ${LANG}</span>`);
                });

                it('добавляются все переводы по подключу c условным оператором', function () {
                    execView(bundle.localeCondition, {val: true}).should.contain(`<span class="locale__test">test1${LANG}</span>`);
                    execView(bundle.localeCondition, {val: false}).should.contain(`<span class="locale__test">test2${LANG}</span>`);

                    execView(bundle.getlocaleByKey('condition.notUsed')).should.contain(`<span class="locale__test">notUsed${LANG}</span>`);
                });

                it('заменяются вызовы home.l10n', function () {
                    bundle.testClient().should.contain(`<span class="locale__test">client${LANG}</span>`);
                });

                it('заменяются прямые импорты l10n', function () {
                    bundle.testDirectImport().should.contain(`direct${LANG}`);
                });

                it('заменяются прямые импорты l10n по частично вычисляемому ключу', function () {
                    bundle.evalDirectImport('one').should.contain(`evalDirect${LANG}`);
                });

                it('заменяет вызовы внутри try-catch', function () {
                    bundle.tryCatch().should.contain('try');
                });

                it('заменяются переводы по подключу, если в сборке уже есть вложенный ключ', function () {
                    execView(bundle.localeNestedDepth).should.contain(`nestedDepthTest1${LANG}nestedDepthTest2${LANG}`);
                });

                describe('работают экспорты', function () {
                    it('single экспорт плоского ключа', function () {
                        execView(bundle.getlocaleByKey('singleExportVariable')).should.contain(`<span class="locale__test">singleExportVariable${LANG}</span>`);
                    });

                    it('single экспорт иерархического ключа', function () {
                        execView(bundle.getlocaleByKey('nested.singleExportVariable')).should.contain(`<span class="locale__test">nestedSingleExportVariable${LANG}</span>`);
                    });

                    it('default экспорт плоского ключа', function () {
                        execView(bundle.getlocaleByKey('defaultExportVariable')).should.contain(`<span class="locale__test">defaultExportVariable${LANG}</span>`);
                    });

                    it('default экспорт иерархического ключа', function () {
                        execView(bundle.getlocaleByKey('nested.defaultExportVariable')).should.contain(`<span class="locale__test">nestedDefaultExportVariable${LANG}</span>`);
                    });

                    it('массивов склонений с числами', function () {
                        execView(bundle.localeExportArray).should.contain(`<span class="locale__test">export one ${LANG}, export two ${LANG}, export more ${LANG}</span>`);
                    });
                });

            });

        });

    });

    describe('l10n на серверсайде', function () {
        let req,
            bundle;

        beforeEach(function () {
            req = {};
            req.l10n = function (path, optionalLang) {
                return getTranslation(path, optionalLang || req.Locale);
            };

            bundle = require('./server-side/bundles/server.js');
        });

        describe('по плоскому ключу', function () {
            it('работает один язык', function () {
                req.Locale = 'ru';
                bundle.locale({}, req).should.contain('<span class="locale__test">testRU</span>');
            });

            it('работает другой язык', function () {
                req.Locale = 'en';
                bundle.locale({}, req).should.contain('<span class="locale__test">testEN</span>');
            });

            it('не работает, если нет в конфиге', function () {
                req.Locale = 'no_lang';
                bundle.locale({}, req).should.contain('<span class="locale__test"></span>');
            });

            it('заменяются массивы склонений с числами', function () {
                req.Locale = 'en';
                bundle.localeArray({}, req).should.contain('<span class="locale__test">one EN-two EN-more EN</span>');
            });
        });

        describe('по иерархическому ключу', function () {
            it('работает один язык', function () {
                req.Locale = 'ru';
                bundle.localeNested({}, req).should.contain('<span class="locale__test">nestedTestRU</span>');
            });

            it('работает другой язык', function () {
                req.Locale = 'en';
                bundle.localeNested({}, req).should.contain('<span class="locale__test">nestedTestEN</span>');
            });

            it('не работает, если нет в конфиге', function () {
                req.Locale = 'no_lang';
                bundle.localeNested({}, req).should.contain('<span class="locale__test"></span>');
            });
        });

    });
});
