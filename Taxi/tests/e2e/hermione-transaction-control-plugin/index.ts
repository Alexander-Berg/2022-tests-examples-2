import got from 'got';
import type Hermione from 'hermione';
import {buildTestUrl} from 'tests/e2e/utils/build-test-url';
import {v4 as uuidv4} from 'uuid';

import {routes} from 'service/transaction-controller';

function plugin(hermione: Hermione) {
    hermione.on(hermione.events.RUNNER_START, async function () {
        await got.post(buildTestUrl(routes.destroy()));
        await got.post(buildTestUrl(routes.initialize()));
    });

    hermione.on(hermione.events.AFTER_TESTS_READ, function (collection) {
        collection.eachRootSuite(function (root) {
            void root.beforeEach(async function (this: Mocha.IBeforeAndAfterContext) {
                this.currentTest.uuid = uuidv4();
                await got.post(buildTestUrl(routes.beginTransaction(this.currentTest.uuid)));
            });

            void root.afterEach(async function (this: Mocha.IBeforeAndAfterContext) {
                await got.post(buildTestUrl(routes.rollbackTransaction(this.currentTest.uuid)));
            });
        });
    });

    hermione.on(hermione.events.RUNNER_END, async function () {
        await got.post(buildTestUrl(routes.destroy()));
    });
}

module.exports = plugin;
