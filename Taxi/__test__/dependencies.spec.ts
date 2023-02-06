import { DependenciesTree, FilesAST } from '../../../types';
import { collectUsedContent, invertDependenciesTree, reduceDependenciesPath, reducePath } from '../dependencies';

describe('utils/yaml/dependencies', () => {
    test('invertDependenciesTree', () => {
        expect(
            invertDependenciesTree({
                a: {
                    b: [],
                    c: [],
                },
                b: {
                    d: [],
                    e: [],
                },
                e: {
                    c: [],
                },
            }),
        ).toEqual({
            a: [],
            b: ['a'],
            c: ['a', 'e'],
            d: ['b'],
            e: ['b'],
        });
    });

    test('collectUsedContent', () => {
        expect(
            collectUsedContent({
                '/a/b/c/d/1.yaml': {},
                '/a/b/c/e/2.yaml': {},
            }),
        ).toEqual({
            '/a/b/c/d': {
                files: { '/a/b/c/d/1.yaml': true },
                folders: {},
            },
            '/a/b/c': {
                files: {},
                folders: { d: true, e: true },
            },
            '/a/b': {
                files: {},
                folders: { c: true },
            },
            '/a': {
                files: {},
                folders: { b: true },
            },
            '/a/b/c/e': {
                files: { '/a/b/c/e/2.yaml': true },
                folders: {},
            },
        });
    });

    test('reducePath', async () => {
        const repoRoot = '/Users/ktnglazachev/projects/taxi-typings/src/utils/yaml/__test__/specs/repo';
        const file1 = `${repoRoot}/service1/docs/yaml/definitions.yaml`;
        const file2 = `${repoRoot}/service1/docs/yaml/api/api.yaml`;
        const file3 = `${repoRoot}/service2/docs/yaml/definitions.yaml`;

        expect(
            await reducePath(
                file1,
                repoRoot,
                collectUsedContent({
                    [file1]: {},
                    [file2]: {},
                }),
            ),
        ).toBe(`${repoRoot}/definitions.yaml`);

        expect(
            await reducePath(
                file2,
                repoRoot,
                collectUsedContent({
                    [file1]: {},
                    [file2]: {},
                    [file3]: {},
                }),
            ),
        ).toBe(`${repoRoot}/service1/api/api.yaml`);
    });

    test('reduceDependenciesPath', async () => {
        const repoRoot = '/Users/ktnglazachev/projects/taxi-typings/src/utils/yaml/__test__/specs';

        const file1 = `${repoRoot}/plain-type.yaml`;
        const file2 = `${repoRoot}/repo/service/docs/yaml/api/api.yaml`;
        const file3 = `${repoRoot}/repo/service/docs/yaml/definitions.yaml`;
        const file4 = `${repoRoot}/repo/service/docs/yaml/api/1.yaml`;

        const expectFile2 = `${repoRoot}/repo/api/api.yaml`;
        const expectFile3 = `${repoRoot}/repo/definitions.yaml`;
        const expectFile4 = `${repoRoot}/repo/api/1.yaml`;

        const empty = {
            types: {},
            imports: [],
        };

        const dependenciesTree: DependenciesTree = {
            [file1]: {
                [file2]: [],
            },
            [file2]: {
                [file3]: [],
            },
            [file3]: {},
            [file4]: {},
        };

        const filesAST: FilesAST = {
            [file1]: empty,
            [file2]: empty,
            [file3]: empty,
            [file4]: empty,
        };

        await reduceDependenciesPath({ dependenciesTree, filesAST, repoRoot });

        expect(dependenciesTree).toEqual({
            [file1]: {
                [expectFile2]: [],
            },
            [expectFile2]: {
                [expectFile3]: [],
            },
            [expectFile3]: {},
            [expectFile4]: {},
        });

        expect(filesAST).toEqual({
            [file1]: empty,
            [expectFile2]: empty,
            [expectFile3]: empty,
            [expectFile4]: empty,
        });
    });
});
