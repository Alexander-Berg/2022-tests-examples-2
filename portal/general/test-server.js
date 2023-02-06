/* eslint no-console: 0 */
/* eslint dot-notation: 0 */
/* eslint new-cap: [2, {"capIsNewExceptions": ["INCLUDE_TEST", "CLEAR_TEST_CACHE"]}] */

const express = require('express');
const request = require('request');
const fs = require('fs');
const http = require('http');
const path = require('path');
const clearModule = require('clear-module');
const hl = require('highlightjs');
const glob = require('glob');
// eslint-disable-next-line node/no-extraneous-require
const fqdn = require('mumu2/lib/fqdn');
const levelsUtil = require('../common/levels');
const config = require('./lib/load-config');
const Stat = require('./lib/stat.js');
const {buildCardResponse, mockZenExport, mockZenConfig} = require('../divcards/tests/builder');
require('colors');

const globalUseWatch = process.argv.slice(2).includes('--watch');
const tmplPath = path.resolve(__dirname, '..');
const staticRoot = path.resolve(__dirname, '..', '..');

const svgMock = "data:image/svg+xml;charset=utf8,%3Csvg xmlns='" +
    "http://www.w3.org/2000/svg' height='10' width='10'%3E%3Cpath " +
    "fill='%23f6ff01' d='M0 0h10v10H0z'/%3E%3Cpath d='M2 6l2 3 5-7' " +
    "fill='none' stroke='%23ff2fe4'/%3E%3C/svg%3E";

const logger = {
    log: function (...args) {
        this.store.push({type: 'log', args});
    },
    info: function (...args) {
        this.store.push({type: 'log', args});
    },
    warn: function (...args) {
        this.store.push({type: 'warn', args});
    },
    error: function (...args) {
        this.store.push({type: 'error', args});
    },
    store: [],
    clear: function () {
        this.store = [];
    }
};

let seal = require('./seal');

const htmlTemplate = fs.readFileSync(__dirname + '/pages/tests/template.html', 'utf-8');
const viewerTemplate = fs.readFileSync(__dirname + '/pages/tests/viewer.html', 'utf-8');
const loggerTemplate = fs.readFileSync(__dirname + '/pages/tests/logger.html', 'utf-8');

const rumTemplate = [
    fs.readFileSync(__dirname + '/../common/libs/node_modules/@yandex-int/rum-counter/dist/inline/interface.js', 'utf-8'),
    fs.readFileSync(__dirname + '/../common/libs/node_modules/@yandex-int/rum-counter/dist/inline/io.js', 'utf-8'),
    fs.readFileSync(__dirname + '/../common/libs/node_modules/@yandex-int/rum-counter/dist/inline/longtask.js', 'utf-8')
].join('');
const rumSettings = {
    beacon: true,
    clck: 'https://yandex.ru/clck/click',
    slots: ['12345,0,0', '54321,0,0'],
    reqid: '99999.2222.333.' + String(Math.random()).substr(2, 12)
};
const rumVars = {
    '287': '213',
    '143': '28.1786'
};
const rum = rumTemplate + ';Ya.Rum.init(' + JSON.stringify(rumSettings) + ',' + JSON.stringify(rumVars) + ');';

// port range [min, max]
let ports;
if ('SANDBOX_TASK_ID' in process.env) {
    // Запуск в сендбоксе
    ports = {min: 19876, max: 19885};
} else {
    // Запуск на деве
    ports = {min: 9876, max: 9885};
}

const getTestObj = function (path, context) {
    if (path.endsWith('.tsx')) {
        context.CLEAR_TEST_CACHE();
        return context.INCLUDE_TEST(path);
    } else {
        clearModule(path);
        return require(path);
    }
};

const getTestData = function (path, name, context) {
    let dataSource = getTestObj(path, context);

    return dataSource[name];
};

const grepTests = function () {
    let res = [];
    let allLevels = levelsUtil.getAllLevels();

    allLevels.forEach(level => {
        res = res.concat(glob.sync(path.resolve(__dirname, '..', level.path) + '/**/*.test-data.+(js|tsx)'));
    });

    return res.map(file => {
        return path.relative(tmplPath, file);
    });
};

function resolveProjects(blockPath) {
    const levelNames = levelsUtil.getBlockViews(blockPath);
    if (!levelNames.length) {
        return [];
    }
    const levelName = levelNames[0];
    const levelDesc = require('../levels.json')[levelName];
    if (!levelDesc) {
        return [];
    }
    if (levelDesc.project) {
        return [levelDesc.project];
    }
    return seal.getProjects();
}

const getBlockInfo = function (blockPath) {
    console.log('getBlockInfo', blockPath);

    const resolvedPath = path.resolve(tmplPath, blockPath);

    return new Promise(resolve => {
        // eslint-disable-next-line node/no-deprecated-api
        fs.exists(resolvedPath, function (res) {
            console.log(resolvedPath, res);

            if (res) {
                let projects = resolveProjects(blockPath);
                const project = projects[0];
                const context = seal.getContextFor(project);
                context.IS_CLIENT = false;
                resolve({
                    data: Object.keys(getTestObj(resolvedPath, context)),
                    levels: levelsUtil.getBlockViews(blockPath),
                    projects: projects
                });
            } else {
                resolve(null);
            }
        });
    });
};

const drawLogger = function (logger) {
    let html = logger.store.map(({args}) => {
        const str = args.map(function (arg) {
            if (typeof arg === 'object') {
                return JSON.stringify(arg, null, 2);
            } else {
                return arg;
            }
        }).join(', ');
        let errString = str;
        const isError = str.includes('Error') && str.includes(' at ');
        let fileStr = '';
        let fileView = '';

        errString = errString.replace(/( at .*?)([^: ()]+\.js)(:)/g, '$1<span class="logger-item__file-link">$2</span>$3');

        if (isError) {
            const lines = str.split('\n');
            const match = lines[1].match(/ at .*?([^: ()]+\.js):(\d+)(?::(\d+))?/) || [];

            if (match[1] && match[2]) {
                const file = match[1];
                const line = Number(match[2]);
                const column = Number(match[3]) || -1;
                let splitted;
                let arrowLine = '';

                fileStr = `${file}:${line}`;
                if (column !== -1) {
                    fileStr += `:${column}`;
                    arrowLine = new Array(column).join(' ') + '^';
                }

                try {
                    fileView = fs.readFileSync(path.resolve(tmplPath, file), 'utf-8');
                    splitted = fileView.split('\n');
                    fileView = splitted.slice(Math.max(0, line - 3), line).concat(arrowLine, splitted.slice(line, line + 4)).join('\n');

                    fileView = `<div class="logger-item__file">${hl.highlight('javascript', fileView).value}</div>`;
                } catch (err) {
                    // file not found
                }
            }
        }

        return `<div class="logger-item">
                <div class="logger-item__title">Error</div>
                <div class="logger-item__stack">${errString}</div>
                ${fileStr && fileView ? `
                    <div class="logger-item__title">${fileStr}</div>
                    <div class="logger-item__fileview">${fileView}</div>
                ` : ''}
            </div>`;
    }).join('');

    const logJson = JSON.stringify(logger.store);

    return loggerTemplate
        .replace('[% html %]', html)
        .replace('[% log %]', logJson);
};

const apiMethods = {
    getBlockInfo: (req, res) => {
        let blockPath = req.query.blockPath;

        getBlockInfo(blockPath).then((result) => {
            res.send(result);
        }).catch(err => {
            console.error(err);
            res.set('Content-Type', 'text/plain; charset=UTF-8');
            res.status(500).send('something happened:\n' + err);
        });
    }
};

const skinInfo = {
    benderViews: {
        dir: 'bender',
        wrap: html => html
    },
    touchViews: {
        dir: 'touch',
        wrap: (html) => {
            return `<div class="content">${html}</div>`;
        }
    }
};

let instance;

exports.run = function (useWatch) {
    useWatch = useWatch || globalUseWatch;

    const app = express();
    let usedPort;

    app.use((req, res, next) => {
        console.log(`Requested ${req.url}`);
        next();
    });

    // обработка тестового ПП запроса
    app.post('/divcards/2/', (req, res, next) => {
        res.status(200).send(buildCardResponse({
            id: req.query.cardId,
            type: req.query.type,
            isDark: req.query.isDark === 'true',
            cards: req.query.cards
        })).end();

        next();
    });

    app.all('/api/v3/launcher/config*', (req, res, next) => {
        res.json(mockZenConfig());

        next();
    });

    app.all('/api/v3/launcher/export*', (req, res, next) => {
        res.json(mockZenExport());

        next();
    });

    app.use(async (req, res, next) => {
        if (!req.query.datafile || !req.query.dataname) {
            next();
            return;
        }
        seal.checkWatch();
        const datafile = path.resolve(tmplPath, req.query.datafile);
        const relativePath = path.relative(tmplPath, datafile);
        const project = req.query.project || resolveProjects(relativePath)[0];
        if (!project) {
            return res.status(500).send(`No project for ${req.query.datafile}`);
        }
        console.log(`${req.query.datafile} in ${project}`);

        const dataParams = req.query.dataParams ? JSON.parse(req.query.dataParams) : null;
        const flags = req.query.flags ? JSON.parse(req.query.flags) : null;
        const dataname = req.query.dataname;
        const query = req.query;

        let html;


        const views = levelsUtil.getBlockViews(relativePath)[0];
        if (!views) {
            next();
            return;
        }
        const blockRoot = levelsUtil.getAllLevels().find(level => level.name === views).path;
        const levelLastDir = blockRoot.split(path.sep).slice(1).join('_');
        const staticDir = path.join('tmpl', blockRoot.split(path.sep).shift(), 'spec', levelLastDir);
        const stat = new Stat({
            yandexuid: '1111111',
            ClckBase: 'https://yandex.ru/clck/',
            RequestId: '1111.1111.1111.1111111',
            logger: console,
            blockdisplayLogger: console,
            statRoot: 'test',
            HomePageNoArgs: 'https://yandex.ru',
            hostname: req.hostname,
            dev: true
        });

        logger.clear();

        let staticHost;

        if (!config.localDev) {
            const ip = (await fqdn()).ip;
            staticHost = `//[${ip}]:${usedPort}`;
        }

        let pageModeList = [];
        let documentMods = ['i-ua_scroll_yes'];

        try {
            const context = seal.getContextFor(project);

            context.IS_CLIENT = false;

            let func = getTestData(datafile, dataname, context);
            let skin;
            let settingsJs;
            let execViewWrapper = function (name, data, req) {
                if (!data) {
                    data = {};
                }
                if (!req) {
                    req = data;
                }

                req.setCounter = stat.setCounter;

                if (!req.l10n) {
                    let locale = req.Locale || levelsUtil.getLang(views);
                    req.l10n = context.home.l10n.bind({Locale: locale});
                }
                if (!req.stat) {
                    req.stat = new context.home.Stat(req, {collect: !!req.offline_page});
                }
                if (!req.ads) {
                    req.ads = new context.home.Ads(req);
                }
                if (!req.settingsJs) {
                    req.settingsJs = settingsJs || context.home.settingsJs({});
                }
                settingsJs = req.settingsJs;

                if (!req.devStaticHost) {
                    req.devStaticHost = staticHost;
                }

                if (!req.getStaticURL) {
                    req.getStaticURL = new context.home.GetStaticURL({
                        devHost: req.devStaticHost,
                        s3root: 's3/home-static'
                    });
                }

                if (!req.resources) {
                    req.resources = new context.home.Resources('test', req, execViewWrapper);
                    req.resources.addBundle = () => '';
                }
                if (!req.csp) {
                    req.csp = new context.home.CSP();
                }

                if (!req.cls) {
                    req.cls = context.home.cls(req);
                }

                if (!req.pageModeList) {
                    req.pageModeList = pageModeList;
                }
                if (!req.pageMods) {
                    req.pageMods = pageModeList;
                }
                if (!req.documentMods) {
                    req.documentMods = pageModeList;
                }

                if (!req.skin) {
                    req.skin = {};
                }
                if (req.Skin) {
                    skin = req.Skin;
                }

                let viewsObj = context.home[views];
                let viewsLocale = req.Locale || levelsUtil.getLang(views);
                if (viewsLocale in viewsObj) {
                    viewsObj = viewsObj[viewsLocale];
                }
                let execView = viewsObj.execView;

                return execView.withReq(name, data, req);
            };
            execViewWrapper.withReq = execViewWrapper;
            if (func) {
                let mockJs = '';
                let opts = {
                    dataParams,
                    flags,
                    query,
                    js: path.join('/', staticDir, '_' + levelLastDir + '.js'),
                    css: path.join('/', staticDir, '_' + levelLastDir + '.css'),
                    additionalCss: [],
                    home: context.home,
                    pageModeList,
                    documentMods
                };
                if (dataParams) {
                    opts.dataParams = dataParams;
                }

                if (dataParams) {
                    opts.flags = flags;
                }

                let res = func(execViewWrapper, opts);
                if (typeof res === 'string') {
                    html = res;
                } else {
                    html = res.html;
                    if (res.htmlMix) {
                        documentMods = Array.isArray(res.htmlMix) ? res.htmlMix : [res.htmlMix];
                    }
                    if (res.bodyMix) {
                        pageModeList = Array.isArray(res.bodyMix) ? res.bodyMix : [res.bodyMix];
                    }
                    if (res.skin) {
                        skin = res.skin;
                    }
                    if (res.mockJs) {
                        mockJs = res.mockJs;
                    }
                }
                let exports = settingsJs ? `<script>${settingsJs.getRawScript()}</script>` : '';

                if (html.indexOf('<body') === -1) {
                    let cssList = opts.additionalCss;
                    let info = skinInfo[views] || {};

                    cssList.unshift(opts.css);

                    if (skin && info.wrap) {
                        html = info.wrap(html);
                    }

                    documentMods.push('document');

                    if (skin === 'night') {
                        documentMods.push('document_dark_yes');
                    }

                    html = htmlTemplate
                        // Проще вернуть значение, чем экранировать
                        .replace('[% html %]', () => html)
                        .replace('[% exports %]', exports)
                        .replace('[% js %]', opts.js)
                        .replace('[% css %]', cssList.map(css => `<link rel="stylesheet" href="${css}">`).join(''))
                        .replace('[% htmlClass %]', documentMods.join(' '))
                        .replace('[% bodyClass %]', pageModeList.join(' '))
                        .replace('[% rum %]', rum)
                        .replace('[% mockJs %]', mockJs)
                        .replace(/\[% mockSvg %]/g, svgMock);
                }
            }
        } catch (err) {
            logger.warn(err + ' > ' + err.stack);
        }

        html = html || 'Data not found';

        if (logger.store.length) {
            html = drawLogger(logger);
        }

        res.send(html);
    });

    app.get('/tests/', (req, res) => {
        let start = Date.now();
        let geminiData = grepTests();
        console.log(`grepTests: ${String(Date.now() - start).yellow} ms`);

        res.set('Content-Type', 'text/html; charset=UTF-8');
        res.send(viewerTemplate.replace('[% data %]', JSON.stringify(geminiData)));
    });

    app.get('/tests-api/', (req, res) => {
        let method = req.query.method;

        if (method in apiMethods) {
            apiMethods[method](req, res);
        } else {
            res.status(400).send({error: 'Unknown api path'});
        }
    });

    app.get('/empty', (req, res) => {
        res.status(200).send('');
    });


    const compression = require('compression');

    app.use(compression());

    if (useWatch) {
        app.use(function (req, res, next) {
            // detector = костыль, чтобы борщик не ругался
            if ((req.path.endsWith('.js') || req.path.endsWith('.css')) && req.path !== '/tmpl/common/detector.inline.js' &&
                req.path !== '/tmpl/common/blocks/home/__load-manager/home__load-manager-inline.js' &&
                !req.path.startsWith('/tmpl/frontend-node/') && !req.path.startsWith('/node_modules/sinon') &&
                !req.path.startsWith('/tmpl/stream-react/.configs/storybook/build/')
            ) {
                const staticPath = path.join(staticRoot, req.path);
                // multibuilder
                const stream = request.get('http://localhost:8086' + staticPath);

                stream.on('error', function () {
                    res.end();
                });

                stream.pipe(res);
            } else {
                next();
            }
        });
    }

    app.use(express.static(staticRoot, {
        maxAge: 5 * 60 * 1000
    }));

    return new Promise(function (resolve, reject) {
        let server = http.createServer(app);
        // порт определяется динамически снаружи и прокидывается аргументом
        let port = config.localDev ? config.listen : ports.min;

        seal.attachLogger(console);
        seal.reload({useWatch});
        seal.attachLogger(logger);

        server.on('error', function (err) {
            if (err.code === 'EADDRINUSE') {
                console.error('EADDRINUSE', port);
                ++port;

                if (port > ports.max) {
                    console.error('All ports are taken');
                    process.exit(1);
                } else {
                    server.listen(port);
                }
            } else {
                reject(err);
            }
        });

        server.listen(port, function () {
            instance = server;
            usedPort = port;
            resolve({port});
        });
    });
};

exports.close = async function close() {
    if (!instance) {
        return;
    }

    instance.close();
    instance = null;
};

const getHostName = function () {
    return new Promise((resolve) => {
        if (config.localDev) {
            resolve({hostname: 'localhost'});
        } else {
            return fqdn().then((params) => {
                resolve(params);
            });
        }
    });
};

if (require.main === module) {
    exports.run().then(({port}) => {
        getHostName().then(({hostname}) => {
            console.log('Listening: ' + `http://${hostname}:${port}/tests/`.yellow);

            // eslint-disable-next-line node/no-unsupported-features/node-builtins
            const inspector = require('inspector');
            const inspectorUrl = inspector.url();

            if (inspectorUrl) {
                require('dns').lookup(require('os').hostname(), function (err, address/*, fam*/) {
                    const slashIndex = inspectorUrl.lastIndexOf('/');
                    const colonIndex = inspectorUrl.lastIndexOf(':');
                    const uuid = inspectorUrl.substring(slashIndex + 1);
                    const port = inspectorUrl.substring(colonIndex + 1, slashIndex);

                    console.log('Devtools page: ' + `devtools://devtools/bundled/js_app.html?experiments=true&v8only=true&ws=[${address}]:${port}/${uuid}`.yellow);
                });
            }
        });
    });
}
