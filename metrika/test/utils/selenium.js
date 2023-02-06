const colors = require('chalk');
const { buildWatch, localServer } = require('./e2e');
const { spawnAsPromised, killFn } = require('../../scripts/utils/proc');

const runMocha = (out, retries, watch) => {
    const args = [];
    if (watch) {
        args.push('--watch');
    } else {
        args.push('--parallel');
    }
    args.push('--reporter', 'mochawesome');
    args.push(
        '--reporter-options',
        'consoleReporter=spec,reportDir=test/e2e/report/selenium,json=false',
    );
    args.push('./test/e2e/selenium-webdriver/*.spec.js');
    const promise = spawnAsPromised('mocha', args, {
        env: Object.assign({}, process.env, {
            YA_SELENIUM_CONF: JSON.stringify(out),
            RETRIES: retries,
            FORCE_COLOR: 1,
        }),
        console: true,
        procName: colors.green('mocha'),
    });
    const kill = killFn(promise.cp, 'mocha');
    process.on('SIGINT', kill.bind(null, 'SIGINT'));
    return promise;
};

const seleniumTestRun = async (
    out,
    killTonel,
    optionCache,
    watch,
    proxyDomains,
    retries,
    pattern,
) => {
    let code = 0;
    const { kill: killWatch, watchEnd } = buildWatch(
        out.inHostname,
        out.port,
        optionCache,
        watch,
        proxyDomains,
        pattern,
    );
    const info = localServer(
        out.port,
        proxyDomains.length ? proxyDomains[0] : out.inHostname,
        proxyDomains,
    );
    const { kill: killServer, promise: serverPromise, readyPromise } = info;
    serverPromise.catch(() => {
        killTonel('selenuim tonel');
    });
    await readyPromise;
    try {
        await watchEnd;
    } catch (e) {
        console.error(colors.red(`Counter build is fail - ${e}`));
    }
    try {
        await runMocha(out, retries, watch);
    } catch (e) {
        console.error(e);
        code = 1;
    }
    killWatch('selenium watch');
    killServer('selenium server');
    return code;
};

module.exports = {
    seleniumTestRun,
};
