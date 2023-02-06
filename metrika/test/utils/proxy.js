const colors = require('chalk');
// eslint-disable-next-line import/no-unresolved
const { spawnAsPromised, killFn } = require('../../scripts/utils/proc');

module.exports = {
    runProxy: (proxyPort, domains, targetHost, targetPort, bundle) => {
        if (!proxyPort) {
            return {
                promise: Promise.resolve(),
                kill: () => {},
            };
        }
        const promise = spawnAsPromised(
            'mitmdump',
            [
                '-s',
                'mitmproxy.py',
                '--ssl-insecure',
                '-p',
                proxyPort,
                '--no-http2',
                '--set',
                'block_global=false',
            ],
            {
                console: true,
                shell: true,
                procName: colors.green('proxy'),
                env: {
                    proxyDomains: JSON.stringify(domains),
                    target: JSON.stringify({
                        host: targetHost,
                        port: targetPort,
                    }),
                    BUNDLE: bundle,
                },
            },
        );
        const kill = killFn(promise.cp, 'proxy');
        promise.catch((e) => {
            kill(`catch ${e}`);
        });
        return {
            promise,
            kill,
        };
    },
};
