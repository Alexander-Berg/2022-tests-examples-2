/**
 * @jest-environment node
 */
import Bottle from 'bottlejs';

import config from '../../../config';
import conductor from '../conductor';
import {CONDUCTOR, CONFIG, GITHUB} from '..';

import Github, {GihubEnhancedApiFactory} from './';

describe('Github', () => {
    const tag = 'rc-0.0.1471';

    const bottle = new Bottle();
    bottle.factory(CONFIG, config);
    bottle.factory(GITHUB, Github);
    bottle.factory(CONDUCTOR, conductor);

    const project = bottle.container[CONFIG].projects['yandex-taxi-tariff-editor'];

    describe('API', () => {
        const {owner, repo} = project.github;
        const api = GihubEnhancedApiFactory(bottle.container[CONFIG].github);

        test('get branches', async () => {
            const results = await api.repos.listBranches({owner, repo});

            expect(results).toHaveProperty('data');
        });

        test('get all branches', async () => {
            const results = await api.customApi.getAllBranches({owner, repo});

            expect(results.find(({name}) => name === 'stable')).toBeTruthy();
        });

        test('get all tags', async () => {
            const results = await api.customApi.getAllTags({owner, repo});

            expect(results.find(({name}) => name.includes('rc-'))).toBeTruthy();
        });

        test('get tag', async () => {
            const results = await api.customApi.getTag(tag, {owner, repo});

            expect(results.tag).toBe(tag);
            expect(results.message.length).toBeGreaterThan(0);
        });

        test('get all releases', async () => {
            const results = await api.customApi.getAllReleases({owner, repo});

            // TODO  пока нет релизов
            expect(results).toBeTruthy();
        });
    });

    describe('Service', () => {
        const queues = ['TXI'];
        const service = bottle.container[GITHUB](project);

        test('get tickets for tag', async () => {
            const results = await service.getTicketsForTag(tag, queues);
            expect(results).toEqual(['TXI-8979', 'TXI-8131', 'TXI-9251']);
        });

        test('get release branches', async () => {
            const results = await service.getReleaseBranches();
            expect(results.every((branch: any) => branch.name.includes('release-'))).toBe(true);
        });

        test('get release candidate branches', async () => {
            const results = await service.getReleaseCandidateBranches();
            expect(results.every((branch: any) => branch.name.includes('rc-'))).toBe(true);
        });

        test('get tags for release', async () => {
            const originMethod = service.getLastReleaseVersion;
            service.getLastReleaseVersion = () => Promise.resolve('0.0.1452.1');

            try {
                const results = await service.getTagsForRelease('0.0.1463.1');
                expect(results.length).toBe(11);
                expect(results[0].name).toBe('rc-0.0.1453');
                expect(results.pop().name).toBe('rc-0.0.1463');
            } finally {
                service.getLastReleaseVersion = originMethod;
            }
        });

        test('get tickets for release', async () => {
            const currentRelease = '0.0.1452.1';

            const originGitMethod = service.getLastReleaseVersion;
            service.getLastReleaseVersion = () => Promise.resolve(currentRelease);

            // versions[pkg].stable.version
            const originConductorMethod = bottle.container[CONDUCTOR].package.versions;
            bottle.container[CONDUCTOR].package.versions = () =>
                Promise.resolve({
                    [project.id]: {
                        stable: {
                            version: currentRelease
                        }
                    }
                } as any);

            try {
                const results = await service.getTicketsForRelease('0.0.1463.1', queues);
                expect(results.sort()).toEqual(
                    [
                        'TXI-8285',
                        'TXI-9216',
                        'TXI-9233',
                        'TXI-8933',
                        'TXI-9092',
                        'TXI-8809',
                        'TXI-9091',
                        'TXI-8996',
                        'TXI-7805',
                        'TXI-9196',
                        'TXI-9183',
                        'TXI-9189'
                    ].sort()
                );
            } finally {
                service.getLastReleaseVersion = originGitMethod;
                bottle.container[CONDUCTOR].package.versions = originConductorMethod;
            }
        });
    });
});
