const chokidar = require('chokidar');
const colors = require('chalk');
// eslint-disable-next-line import/no-unresolved
const { spawnAsPromised, killFn } = require('../../scripts/utils/proc');

const buildWatch = (
    host,
    port,
    disable,
    watch,
    proxyList,
    pattern,
    isSmokeTest,
) => {
    if (disable) {
        return {
            kill: () => {},
            promise: Promise.resolve(),
        };
    }
    const bundle = isSmokeTest ? 'prod' : 'e2e';
    const promise = spawnAsPromised(
        './build.ts',
        ['--bundle', bundle]
            .concat(watch ? ['--watch'] : [])
            .concat(pattern ? ['--files'].concat(pattern) : [])
            .concat(proxyList.length ? [] : ['--host', `${host}:${port}`]),
        {
            console: true,
            fork: true,
            procName: colors.rgb(200, 255, 200)('buildProc'),
            execArgv: [
                '-r',
                'ts-node/register',
                '-r',
                'tsconfig-paths/register',
                '--max-old-space-size=4000',
            ],
            env: {
                TS_NODE_FILES: true,
                FORCE_COLOR: 1,
            },
        },
    );
    const kill = killFn(promise.cp, 'watch');
    promise.catch(() => {
        kill('catch');
    });
    const watchEnd = new Promise((resolve, reject) => {
        promise.catch(reject);
        promise.cp.on('exit', () => {
            resolve();
        });
        promise.cp.on('message', (code) => {
            if (code === 'END') {
                resolve();
            }
        });
    });
    process.on('SIGINT', kill.bind(null, 'SIGINT'));
    return {
        kill,
        promise,
        watchEnd,
    };
};

const localServer = (port, host, domains, isHTTP = true) => {
    const promise = spawnAsPromised(
        'npm',
        ['run', 'test:server'].concat(isHTTP ? ['--', '--', '--http'] : []),
        {
            console: true,
            env: Object.assign({}, process.env, {
                testHostName: host,
                FORCE_COLOR: 1,
                testPort: port,
                domains: JSON.stringify(domains),
            }),
            procName: colors.rgb(100, 255, 100)(`Web Server ${port}`),
        },
    );
    const kill = killFn(promise.cp, 'server');
    let isKilled = false;
    const killWrapper = (...args) => {
        isKilled = true;
        return kill(...args);
    };
    promise.catch(() => {
        killWrapper('catch');
    });
    process.on('SIGINT', killWrapper.bind(null, 'SIGINT'));
    const readyPromise = new Promise((resolve, reject) => {
        setTimeout(() => {
            if (isKilled) {
                reject();
            } else {
                resolve();
            }
        }, 1000);
        /* TODO раскоментировать это переделав зпауск сервера co spawn на fork 
        promise.cp.on('message', (message) => {
            if (message == 'ready') {
                resolve()
            }
        }); */
    });
    return {
        kill: killWrapper,
        promise,
        readyPromise,
    };
};
const callHerminone = (out, isProxy, retries, set, isSmokeTest) => {
    let hermioneConfigName;
    if (isSmokeTest) {
        hermioneConfigName = '.smoke';
    } else {
        hermioneConfigName = isProxy ? '.proxy' : '';
    }

    const args = [
        '--config',
        `./test/e2e/hermione${hermioneConfigName}.conf.js`,
    ];
    if (set) {
        args.push('--set', set);
    }

    // гоним тесты сборки кода счетчика через локальный сервер
    return spawnAsPromised('hermione', args, {
        env: Object.assign({}, process.env, {
            YA_SELENIUM_CONF: JSON.stringify(out),
            RETRIES: retries,
            FORCE_COLOR: 1,
        }),
        console: true,
        procName: colors.rgb(255, 206, 21)('hermione'),
    });
};

const startFileWatch = (out, kill, isProxy, retries, set, isSmokeTest) => {
    const nodeInf = chokidar.watch('./test/e2e', {
        ignored: ['./test/e2e/report'],
    });
    return {
        startWatch: (watchChildProcess) =>
            new Promise((resolve, reject) => {
                if (!watchChildProcess) {
                    reject(new Error('Empty child process'));
                }
                watchChildProcess.on('message', (message) => {
                    if (message === 'END') {
                        console.log(
                            colors.green(`Restart hermione watch build`),
                        );
                        callHerminone(
                            out,
                            isProxy,
                            retries,
                            set,
                            isSmokeTest,
                        ).catch(() => {
                            console.log(colors.red('Hermione fail'));
                        });
                    }
                });
                nodeInf.on('change', (path) => {
                    console.log(
                        colors.green(`Restart hermione change ${path}`),
                    );
                    callHerminone(
                        out,
                        isProxy,
                        retries,
                        set,
                        isSmokeTest,
                    ).catch(() => {
                        console.log(colors.red('Hermione fail'));
                    });
                });
                process.on('SIGINT', () => {
                    resolve();
                });
            }),
        kill: () => {
            nodeInf.close();
        },
    };
};

module.exports = {
    buildWatch,
    localServer,
    startFileWatch,
    e2eTestRun: async (
        out,
        killTonel,
        buildCounter,
        watch,
        proxyDomains,
        retries,
        set,
        pattern,
        isSmokeTest,
        noRebuild = false,
    ) => {
        let code = 0;
        // запускаем сборку кода счетчика
        const {
            kill: killWatch,
            watchEnd,
            promise: watchPromise,
        } = noRebuild
            ? {
                  kill: () => {},
                  watchEnd: Promise.resolve(),
                  promise: Promise.resolve(),
              }
            : buildWatch(
                  out.inHostname,
                  out.port,
                  buildCounter,
                  watch,
                  proxyDomains,
                  pattern,
                  isSmokeTest,
              );
        // запускаем локальный сервер
        const info = localServer(
            out.port,
            proxyDomains.length ? proxyDomains[0] : out.inHostname,
            proxyDomains,
        );
        const { kill: killServer, promise: serverPromise } = info;

        let killDeviceServer = () => {};

        if (out.port !== 30102 && proxyDomains.length) {
            const deviceNode2 = localServer(
                30103,
                proxyDomains.length ? proxyDomains[0] : out.inHostname,
                proxyDomains,
                false,
            );
            const deviceNode3 = localServer(
                29010,
                proxyDomains.length ? proxyDomains[0] : out.inHostname,
                proxyDomains,
                false,
            );
            killDeviceServer = (log) => {
                deviceNode2.kill(log);
                deviceNode3.kill(log);
            };
        }

        const kill = (log) => {
            killTonel(log);
            killServer(log);
            killWatch(log);
            killDeviceServer(log);
        };

        serverPromise.catch(() => {
            killTonel('e2e server');
        });

        try {
            await watchEnd;
        } catch (e) {
            console.error(colors.red(`Counter build is fail - ${e}`));
        }
        const promise = callHerminone(
            out,
            proxyDomains.length,
            retries,
            set,
            isSmokeTest,
        );
        try {
            await promise;
        } catch (e) {
            console.error(colors.red(`Hermione call is fail - ${e}`));
            code = 1;
        }
        if (watch) {
            const { kill: killWatchFiles, startWatch } = startFileWatch(
                out,
                kill,
                proxyDomains.length,
                retries,
                set,
                isSmokeTest,
            );
            await startWatch(watchPromise.cp);
            killWatchFiles();
        }
        kill('e2e finish');
        return code;
    },
};
