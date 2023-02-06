const commandLineArgs = require('command-line-args');
const os = require('os');
// eslint-disable-next-line import/no-unresolved
const { tunnel } = require('../scripts/utils/tunnel');

const { env } = process;
const {
    e2eTestRun,
    seleniumTestRun,
    last,
    versionList,
    runProxy,
} = require('./utils');
// eslint-disable-next-line import/no-unresolved
const { spawnAsPromised } = require('../scripts/utils/proc');

let inHostname = 'selenium-tunnel.vla.yp-c.yandex.net';
const inBrowsers = ['selenium'];
let userPass = env.SELENIUM_PASSWORD;
let returnCode = 0;
const proxyDomains = [
    'mc\\.yandex\\.ru', // должен быть первым для работы socket
    '2724587256\\.mc\\.yandex\\.ru', // rostelecom
    'adstat\\.yandex\\.ru', // megafon
    'mc\\.yandex\\.com',
    'mc\\.webvisor\\.org', // ua
    '127\\.0\\.0\\.1',
    'mc\\.yandex\\.com\\.tr',
    'mc\\.yandex\\.md',
    'ymetrica1.com',
    'yandexmetrica\\.com',
    'yandex\\.ru',
    'yandex\\.com',
    'yandex\\.com\\.tr',
    'example\\.com',
    'mm\\.mtproxy\\.yandex\\.net', // что-то вроде metrika player
    'metrika.yandex.ru',
    'yastatic\\.net',
    'metrika\\.yandex\\.ru',
];

const check = async (no = 1, options) => {
    let port = 8138;
    const domains = options.proxy ? proxyDomains : [];
    let proxyPort = domains.length ? 8084 : 0;
    let secret;
    let tunnelConnection = {
        kill: () => {},
    };
    let proxyRun;
    let proxyTonel;
    let useGrid = true;
    const bundle = options.smoke ? 'prod' : 'e2e';

    if (options.local) {
        inHostname = 'localhost';
        proxyRun = runProxy(proxyPort, domains, inHostname, port, bundle);
        useGrid = false;
    } else if (env.DISABLE_DEV_SSH_TUNNEL) {
        const ifaces = os.networkInterfaces().eth0;
        const { address } =
            ifaces.find(
                ({ internal, family, scopeid }) =>
                    !internal && family === 'IPv6' && scopeid === 0,
            ) || {};
        if (address) {
            inHostname = `[${address}]`;
        }

        proxyRun = runProxy(proxyPort, domains, 'localhost', port, bundle);
    } else {
        if (no === 3) {
            throw new Error(
                `after ${no} retries we can't establish ssh tunnel`,
            );
        }
        try {
            await spawnAsPromised('ya', ['vault', '--help']);
        } catch (e) {
            console.log(`Catch check ${e}`);

            console.log('///////////////////////');
            console.log('Ya не установлен');
            console.log(
                'Инструкция по установке -',
                'https://nda.ya.ru/3VqhPL',
            );
            console.log('///////////////////////');
        }

        const rawData = await versionList(env.npm_package_config_vault);
        if (!rawData) {
            console.error('SSH creds error');
            return;
        }
        secret = await last(rawData.secret_versions[0].version);
        userPass = secret.value.seleniumPassword;
        // if (options.set) {
        tunnelConnection = tunnel(inHostname);
        ({ port } = tunnelConnection);
        // }
        if (proxyPort) {
            proxyTonel = tunnel(inHostname);
            proxyPort = proxyTonel.port;
            proxyRun = runProxy(proxyPort, domains, inHostname, port, bundle);
        }
    }

    const out = {
        port,
        domains,
        proxyPort,
        userPass: `metrika:${userPass}`,
        useGrid,
        pattern: options.pattern,
        inBrowsers,
        inHostname,
    };

    console.log(`HOSTNAME IS ${inHostname}`);
    console.log(`PORT IS ${port}`);
    console.log(`USE GRID ${useGrid}`);

    if (options.selenium) {
        returnCode = await seleniumTestRun(
            out,
            tunnelConnection.kill,
            options.cache,
            options.watch,
            domains,
            options.retries,
            options.pattern,
        );
    } else if (options.e2e) {
        // Для test/common тестов запускать по умолчанию только common set
        const set =
            options.local && !options.proxy && !options.set
                ? 'common'
                : options.set;

        returnCode = await e2eTestRun(
            out,
            tunnelConnection.kill,
            options.cache,
            options.watch,
            domains,
            options.retries,
            set,
            options.pattern,
            options.smoke,
            options.noRebuild,
        );
    }
    tunnelConnection.kill('after run');
    proxyRun && proxyRun.kill('kill proxy');
    proxyTonel && proxyTonel.kill('kill tonel');

    // eslint-disable-next-line consistent-return
    return out;
};

if (!module.parent) {
    const options = commandLineArgs([
        { name: 'watch', alias: 'w', type: Boolean },
        { name: 'cache', alias: 'c', type: Boolean },
        { name: 'e2e', alias: 'e', type: Boolean },
        { name: 'local', alias: 'l', type: Boolean },
        { name: 'pattern', alias: 'p', type: String, multiple: true },
        { name: 'proxy', alias: 'x', type: Boolean },
        { name: 'retries', alias: 'r', type: Number },
        { name: 'set', alias: 's', type: String },
        { name: 'smoke', alias: 'k', type: Boolean },
        { name: 'noRebuild', alias: 'n', type: Boolean },
        { name: 'selenium', alias: 'i', type: Boolean },
    ]);

    check(0, options)
        .then(() => {
            console.log('Finish');
            if (!options.local) {
                process.exitCode = returnCode;
            }
        })
        .catch((code) => {
            console.error(`Catch - ${code}`);
            console.error(code);
            process.exitCode = 1;
        });
}
