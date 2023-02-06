const typescript = require('typescript');

const colors = require('chalk');

const errorPrefix = `err:`;
const SOCKET_ERROR = `${errorPrefix} Socket does't exist`;
const TIMEOUT_ERROR = `${errorPrefix} Timeout script execution`;
const CODE_ERROR = `${errorPrefix} code error `;
const asyncConfig = process.env.YA_SELENIUM_CONF
    ? JSON.parse(process.env.YA_SELENIUM_CONF)
    : {};

const DEFAULT_REQUEST_REGEXP = '\\/watch\\/\\d+';
const WEBVISOR_REQUEST_REGEXP = '\\/webvisor\\/\\d+';
const CLICKMAP_REQUEST_REGEXP = '\\/clmap\\/\\d+';

const REGEXPS = {
    defaultRequestRegEx: DEFAULT_REQUEST_REGEXP,
    webvisorRequestRegEx: WEBVISOR_REQUEST_REGEXP,
    clickmapRequestRegEx: CLICKMAP_REQUEST_REGEXP,
};

module.exports = {
    REGEXPS,
    stringifyFunctions(fnList) {
        return fnList.reduce((acc, fn) => {
            const dict = acc;
            dict[fn.name] = this.stringifyFn(fn);
            return dict;
        }, {});
    },
    stringifyFn(fn) {
        if (typeof fn !== 'function') {
            const errorMessage = colors.red(
                'a value of type other than function provided to stringifyFn',
            );
            console.log(errorMessage);
            return null;
        }

        let source = fn.toString().trim();

        if (!source.startsWith('function')) {
            source = `function ${source}`;
        }

        return typescript
            .transpileModule(source, {
                compilerOptions: { removeComments: true },
            })
            .outputText.replace(/\n/g, '');
    },
    provideServerHelpers(browser, rawOptionsUp) {
        const cb =
            rawOptionsUp.cb ||
            function (a, b, done) {
                done(CODE_ERROR);
            };
        const optionsUp = {
            regexp: REGEXPS,
            ...rawOptionsUp,
            error: {
                socket: SOCKET_ERROR,
                timeout: TIMEOUT_ERROR,
                code: CODE_ERROR,
            },
        };
        return () =>
            browser.executeAsync(
                /* 
                    Этот код должен работать в старых браузерах
                    они очень бояться trailing comma и прочих стрелок
                */
                /* eslint-disable */
                function (options, fns, cb, done) {
                    function bind(fn) {
                        var args = [].slice.call(arguments).slice(1);
                        return function () {
                            var args2 = [].slice.call(arguments);
                            return fn.apply(this, args.concat(args2));
                        };
                    }
                    function run() {
                        window._testTimeout;
                        var helpers = {};
                        for (fnStr in fns)
                            if (fns.hasOwnProperty(fnStr)) {
                                var resFn = 'return ' + fns[fnStr];
                                try {
                                    helpers[fnStr] = new Function(resFn)();
                                } catch (e) {
                                    done(options.error.code + fnStr);
                                    return;
                                }
                            }
                        try {
                            var testFn = new Function('return ' + cb)();
                        } catch (e) {
                            done(options.error.code + ' testFn' + e.stack);
                            return;
                        }
                        var bindedOnRequestFn = bind(
                            helpers.onRequest,
                            options,
                            window,
                            done
                        );
                        testFn(
                            {
                                onRequest: bindedOnRequestFn,
                                addRule: bind(
                                    helpers.addRule,
                                    options,
                                    window,
                                    done
                                ),
                                collectRequests: bind(
                                    helpers.collectRequests,
                                    bindedOnRequestFn,
                                    done
                                ),
                                collectRequestsForTime: bind(
                                    helpers.collectRequestsForTime,
                                    bindedOnRequestFn,
                                    done
                                ),
                            },
                            options,
                            done
                        );
                    }
                    if (!window._socket) {
                        window.addEventListener('socket', function () {
                            if (!window._socket) {
                                done(options.error.socket);
                            } else {
                                run();
                            }
                        });
                    } else {
                        run();
                    }
                },
                /* eslint-enable */
                optionsUp,
                this.stringifyFunctions([
                    this.addRule,
                    this.collectRequests,
                    this.onRequest,
                    this.collectRequestsForTime,
                ]),
                this.stringifyFn(cb),
            );
    },
    addRule: function addRule(options, ctx, done, ruleParam, callback) {
        const rules = Array.isArray(ruleParam) ? ruleParam : [ruleParam];
        if (!ctx._socket) {
            done(options.error.socket);
        }
        let rulesAddedCount = 0;
        rules.forEach(function (rule) {
            const requestId = Math.round(
                Math.random() * Number.MAX_SAFE_INTEGER,
            );
            const successCallback = function (data) {
                if (data.requestId === requestId) {
                    rulesAddedCount += 1;
                    ctx._socket.off('success:addRule', successCallback);
                    if (rulesAddedCount === rules.length) {
                        callback();
                    }
                }
            };

            if (typeof rule.body === 'object') {
                rule.headers = rule.headers || {};
                rule.headers['content-type'] = 'application/json';
                rule.body = JSON.stringify(rule.body);
            }

            rule.requestId = requestId;

            ctx._socket.on('success:addRule', successCallback);
            ctx._socket.emit('addRule', rule);
        });
    },
    // функция передается как строка по этому нужно
    // держать ее чистой без сайд эффектов
    onRequest: function onRequest(options, ctx, done, cb, filterRegexString) {
        if (!ctx._socket) {
            done(options.error.socket);
        }
        const originalCallback = cb || function () {};
        const requestWrapper = function (request) {
            if (typeof filterRegexString === 'string') {
                if (new RegExp(filterRegexString).test(request.url)) {
                    originalCallback(request);
                }
            } else {
                originalCallback(request);
            }
        };
        ctx._socket.on('request', requestWrapper);
        ctx._socket.emit('clientReady');
    },
    // собрать запросы за время
    collectRequestsForTime(onRequest, done, time, filterRegexString) {
        const requests = [];
        onRequest(function (request) {
            requests.push(request);
        }, filterRegexString);

        setTimeout(function () {
            done(requests);
        }, time);
    },
    // собрать запросы по дебаунсу
    collectRequests: function collectRequests(
        onRequest,
        done,
        time,
        cb,
        filterRegexString,
    ) {
        let timeout = setTimeout(function () {
            if (cb) {
                cb([], done);
            } else {
                done([]);
            }
        }, time);
        const requests = [];

        onRequest(function (request) {
            requests.push(request);
            clearTimeout(timeout);
            timeout = setTimeout(function () {
                // requests может быть мутирован после вызова cb
                const finalRequests = [];
                for (let i = 0; i < requests.length; i += 1) {
                    finalRequests.push(requests[i]);
                }

                if (cb) {
                    cb(finalRequests, done);
                } else {
                    done(finalRequests);
                }
            }, time);
        }, filterRegexString);
    },
    handleRequest(browser) {
        return (info = {}) => {
            const extra = {
                log: [],
                js: [],
                net: [],
            };
            return browser
                .log('browser')
                .then(
                    (val) => {
                        (val.value || []).forEach((infoValue = {}) => {
                            let message = `Log source:${
                                infoValue.source
                            } time:${colors.white(
                                infoValue.timestamp,
                            )} - message:${infoValue.message}`;
                            if (infoValue.source === 'console-api') {
                                message = colors.blue(message);
                                extra.log.push(infoValue);
                            } else if (infoValue.source === 'javascript') {
                                message = colors.cyan(message);
                                extra.js.push(infoValue);
                            } else if (infoValue.source === 'network') {
                                extra.net.push(infoValue);
                                if (
                                    (infoValue.message || '').split('jserrs')
                                        .length > 1
                                ) {
                                    message = colors.red(
                                        decodeURIComponent(
                                            infoValue.message.split(
                                                'jserrs',
                                            )[1],
                                        ),
                                    );
                                } else {
                                    message = colors.magenta(message);
                                }
                            } else {
                                message = colors.yellow(message);
                            }
                            console.log(message);
                        });
                    },
                    () => {
                        console.warn('Logs is unavailable');
                    },
                )
                .then(() => {
                    const { value: resp } = info || {};
                    if (resp) {
                        info.extra = extra;
                        if (
                            resp.slice &&
                            resp.slice(0, errorPrefix.length) === errorPrefix
                        ) {
                            console.log(colors.red(resp));
                            throw new Error(resp);
                        }
                        browser.setMeta('log', JSON.stringify(extra));
                    }
                    return info;
                });
        };
    },
    // TODO - delete use extra handleRequest instead
    handleDebugConsole(browser) {
        return () =>
            new Promise((resolve) => {
                browser.log('browser').then((val) => {
                    const consoleMessage = [];

                    (val.value || []).forEach((info = {}) => {
                        let message = `Log source:${info.source} - message:${info.message}`;
                        message = colors.blue(message);

                        if (info.source === 'console-api') {
                            consoleMessage.push(
                                info.message.match(/(\d+:\d+ )(.*)/).pop(),
                            );
                            console.log(message);
                        }
                    });

                    resolve(consoleMessage);
                });
            });
    },
    baseUrl: `http://${asyncConfig.inHostname}:${asyncConfig.port}`,
    goalUrl: `goal://${asyncConfig.inHostname}`,
    formUrl: `form://${asyncConfig.inHostname}`,
    buttonUrl: `btn://${asyncConfig.inHostname}`,
    defaultRequestRegEx: DEFAULT_REQUEST_REGEXP,
    getRequestParams(request) {
        const [url, query = ''] = request.url.split('?');
        const params = query.split('&').reduce((acc, info) => {
            const [key, val] = info.split('=');
            const obj = acc;
            obj[decodeURIComponent(key)] = decodeURIComponent(val);
            return obj;
        }, {});

        const { body } = request;
        let siteInfo = null;

        if (params['site-info'] || body && body['site-info']) {
            try {
                siteInfo = JSON.parse(
                    body && body['site-info'] || params['site-info']
                );
            } catch (e) {}
        }

        const brInfo = {};

        if (params['browser-info']) {
            const paramsBrInfo = params['browser-info'].split(':');
            for (let i = 0; i < paramsBrInfo.length; i += 2) {
                const key = paramsBrInfo[i];
                brInfo[key] = paramsBrInfo[i + 1];
            }
        }

        const telemetry = {};
        if (params.t) {
            params.t
                .split(')')
                .filter(Boolean)
                .forEach((keyVal) => {
                    const [key, val] = keyVal.split('(');
                    telemetry[key] = val;
                });
        }

        const searchCounterId = /[watch|webvisor]\/(\d+)(\/1)?$/.exec(url);
        const counterId = searchCounterId && searchCounterId[1];

        return {
            url,
            params,
            brInfo,
            counterId,
            siteInfo,
            body,
            telemetry,
            headers: request.headers,
        };
    },
    getWebvisorData({ value: requests }) {
        const data = [];
        requests.forEach((request) => {
            const { body } = this.getRequestParams(request);

            if (Array.isArray(body)) {
                body.forEach((value) => {
                    const record = value;
                    try {
                        data.push(record);
                    } catch (e) {
                        // Это не жсон, там какой-то первый запрос в эту ручку пустой
                    }
                });
            }
        });
        return data;
    },
    parseCookie(cookieString) {
        return cookieString.split(';').reduce((rawResult, keyVal) => {
            const result = rawResult;
            const [key, val] = keyVal.split('=');
            result[key.trim()] = decodeURIComponent(val);
            return result;
        }, {});
    },
    querystring(data) {
        return Object.keys(data)
            .reduce((acc, next) => {
                return acc.concat(`${next}=${encodeURIComponent(data[next])}`);
            }, [])
            .join('&');
    },
    findHit(requests, counter, url, exactMatch = true) {
        return requests.some((request) => {
            const { params, counterId } = this.getRequestParams(request);
            const data = params['page-url'];
            return (
                counterId === counter.toString() &&
                (exactMatch ? data === url : data.includes(url))
            );
        });
    },
};
