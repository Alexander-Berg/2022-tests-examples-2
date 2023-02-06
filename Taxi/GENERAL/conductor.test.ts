/**
 * @jest-environment node
 */

import {Conductor, ConductorAPI} from '.';

const TEST_PACKAGE = 'yandex-taxi-tariff-editor';
const TEST_PROJECT = 'taxi';

describe('conductor api', () => {
    let conductor: ConductorAPI = null;
    beforeEach(() => (conductor = Conductor({url: 'https://c.yandex-team.ru/'})));

    test('package.versions', async () => {
        /* eslint-disable-next-line no-console */
        console.info(await conductor.package.versions(TEST_PACKAGE));
        expect(await conductor.package.versions(TEST_PACKAGE)).toHaveProperty(TEST_PACKAGE);
    });

    test('package.tickets', async () => {
        expect((await conductor.package.tickets.all(TEST_PACKAGE)).length).toBeGreaterThan(0);
    });

    test('project.hosts', async () => {
        expect((await conductor.project.hosts([TEST_PROJECT])).length).toBeGreaterThan(0);
    });

    test('package.version', async () => {
        expect(await conductor.package.version(TEST_PACKAGE)).toHaveProperty(TEST_PACKAGE);
    });

    test('package.tickets.sinceLastRelease', async () => {
        /* eslint-disable-next-line no-console */
        console.info(await conductor.package.tickets.sinceLastRelease(TEST_PACKAGE));
    });

    test('package.tickets.forNewRelease', async () => {
        /* eslint-disable-next-line no-console */
        console.info(
            await conductor.package.tickets.forVersion(['TXI'], {
                package: TEST_PACKAGE,
                version: '0.0.672'
            })
        );
    });
});
