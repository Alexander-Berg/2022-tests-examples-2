import exec from 'child_process';
import got from 'got';
import type Hermione from 'hermione';
import {getPort, getPorts} from 'tests/e2e/load-balancer';
import buildServerUrl from 'tests/e2e/utils/build-server-url';
import {v4 as uuidv4} from 'uuid';

import {routes} from 'service/transaction-controller';

function plugin(hermione: Hermione) {
    let ports: number[] = [];

    hermione.on(hermione.events.INIT, async function () {
        ports = await getPorts();
    });

    hermione.on(hermione.events.RUNNER_START, async function () {
        await Promise.all(
            ports.map(async (port) => {
                await got.post(buildServerUrl(routes.destroy(), port));
                await got.post(buildServerUrl(routes.initialize(), port));
            })
        );
    });

    hermione.on(hermione.events.AFTER_TESTS_READ, function (collection) {
        collection.eachRootSuite(function (root) {
            void root.beforeEach(async function (this) {
                this.currentTest.uuid = uuidv4();
                this.currentTest.port = await getPort();
                await got.post(buildServerUrl(routes.beginTransaction(this.currentTest.uuid), this.currentTest.port));
            });

            void root.afterEach(async function (this) {
                await got.post(
                    buildServerUrl(routes.rollbackTransaction(this.currentTest.uuid), this.currentTest.port)
                );
            });
        });
    });

    hermione.on(hermione.events.RUNNER_END, async function () {
        await Promise.all(ports.map((port) => got.post(buildServerUrl(routes.destroy(), port))));
    });

    hermione.on(hermione.events.EXIT, function () {
        exec.execSync(ports.map((port) => `curl -X POST -s ${buildServerUrl(routes.destroy(), port)}`).join(' & '));
    });
}

module.exports = plugin;
