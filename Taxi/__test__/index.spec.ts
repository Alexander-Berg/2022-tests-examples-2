import fs from 'fs';
import path from 'path';

import {
    checkout,
    getDeclarationFilePath,
    getRepositoryConfig,
    getSpecsPath,
    parseScope,
    readConfig,
    resolveContext,
} from '..';
import { CliOptions, Config, FullConfig } from '../../types';
import { createPluginComposite } from '../plugins';

const CLI_OPTIONS: CliOptions = {
    context: __dirname,
    config: 'test-config.json',
};

const FULL_CONFIG: FullConfig = {
    ...CLI_OPTIONS,
    ...readConfig(CLI_OPTIONS),
    scope: undefined,
    plugins: createPluginComposite([]),
};

describe('utils/index', () => {
    test('resolveContext', () => {
        expect(resolveContext(__dirname)).toBe(__dirname);
        expect(resolveContext('./src/utils/__test__')).toBe(__dirname);
    });

    test('getSpecsPath git', () => {
        const fullConfig = { ...FULL_CONFIG };
        fullConfig.context = __dirname;
        fullConfig.specsDir = './api/yaml';

        expect(getSpecsPath(fullConfig.repositories[0], fullConfig)).toBe(`${__dirname}/api/yaml`);
    });

    test('getSpecsPath arc', () => {
        const fullConfig = { ...FULL_CONFIG };
        fullConfig.context = __dirname;

        expect(getSpecsPath(fullConfig.repositories[1], fullConfig)).toBe(`${process.env.HOME}/arc/taxi/uservices`);
    });

    test('readConfig json format', () => {
        const config = readConfig(CLI_OPTIONS);
        const expected: Config = {
            specsDir: 'specs',
            typingsDir: 'typings',
            mountDir: '~/arc',
            repositories: [
                {
                    vcs: 'git',
                    name: 'backend-py3-git',
                    branch: 'develop',
                    checkout: ['services/admin-users-info/docs/yaml/api'],
                    targets: {
                        test: ['services/admin-users-info/docs/yaml/api'],
                    },
                    url: 'https://github.yandex-team.ru/taxi/backend-py3',
                    useShortPaths: true,
                },
                {
                    vcs: 'arc',
                    name: 'uservices-arc',
                    branch: 'trunk',
                    targets: {
                        test: ['services/admin-users-info/docs/yaml/api'],
                    },
                    path: 'taxi/uservices',
                    useShortPaths: true,
                },
            ],
        };

        expect(config).toEqual(expected);
    });

    test('readConfig js format', () => {
        const config = readConfig({
            ...CLI_OPTIONS,
            config: 'test-config.js',
        });
        const expected: Config = {
            specsDir: 'specs',
            typingsDir: 'typings',
            mountDir: '~/arc',
            repositories: [
                {
                    vcs: 'git',
                    name: 'backend-py3-git',
                    branch: 'develop',
                    checkout: ['services/admin-users-info/docs/yaml/api'],
                    targets: {
                        test: ['services/admin-users-info/docs/yaml/api'],
                    },
                    url: 'https://github.yandex-team.ru/taxi/backend-py3',
                    useShortPaths: true,
                },
                {
                    vcs: 'arc',
                    name: 'uservices-arc',
                    branch: 'trunk',
                    targets: {
                        test: ['services/admin-users-info/docs/yaml/api'],
                    },
                    path: 'taxi/uservices',
                    useShortPaths: true,
                },
            ],
        };

        expect(config).toEqual(expected);
    });

    test('getRepositoryConfig', () => {
        expect(getRepositoryConfig('backend-py3-git', FULL_CONFIG)).toEqual(FULL_CONFIG.repositories[0]);
    });

    test('checkout git', async () => {
        await checkout('backend-py3-git', FULL_CONFIG);

        const repo = FULL_CONFIG.repositories[0];
        if (repo.vcs !== 'git') {
            throw new Error('git vcs expected');
        }

        const specsPath = getSpecsPath(repo, FULL_CONFIG);
        for (const dir of repo.checkout) {
            const absolutePath = path.join(specsPath, repo.name, dir);
            const exists = fs.existsSync(absolutePath);

            expect(exists).toBe(true);
        }
    }, 100000);

    test('getDeclarationFilePath git', () => {
        const expectedFolder = `${__dirname}/typings/backend-py3-git/service/xxx`;
        expect(
            getDeclarationFilePath(
                FULL_CONFIG.repositories[0],
                `${__dirname}/specs/backend-py3-git/service/xxx/1.yaml`,
                FULL_CONFIG,
            ),
        ).toEqual([expectedFolder, `${expectedFolder}/1.ts`]);
    });

    test('getDeclarationFilePath arc', () => {
        const expectedFolder = `${__dirname}/typings/uservices-arc/service/xxx`;
        expect(
            getDeclarationFilePath(
                FULL_CONFIG.repositories[1],
                `${getSpecsPath(FULL_CONFIG.repositories[1], FULL_CONFIG)}/service/xxx/1.yaml`,
                FULL_CONFIG,
            ),
        ).toEqual([expectedFolder, `${expectedFolder}/1.ts`]);
    });

    test('parseScope', () => {
        expect(parseScope(undefined)).toEqual(undefined);
        expect(parseScope('')).toEqual(undefined);
        expect(parseScope('repo1')).toEqual({ repo1: [] });
        expect(parseScope('repo1:target1:target2 repo2:target1')).toEqual({
            repo1: ['target1', 'target2'],
            repo2: ['target1'],
        });
    });
});
