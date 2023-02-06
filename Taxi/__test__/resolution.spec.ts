import { FilesAST } from '../../../types';
import {
    docsYamlIgnoreResolution,
    localRefResolution,
    RefResolverContextFactory,
    sortRoots,
    sortWeakResolutions,
    strongRefResolution,
} from '../../yaml';

const path2yaml = `${__dirname}/x/y/2.yaml`;
const path1yaml = `${__dirname}/x/y/1.yaml`;
const path3yaml = `${__dirname}/x/y/z/3.yaml`;
const path4yaml = `${__dirname}/a/4.yaml`;
const path5yaml = `${__dirname}/5.yaml`;

const lib1yaml = `${__dirname}/lib1/1.yaml`;
const lib2yaml = `${__dirname}/lib1/docs/yaml/2.yaml`;

const strongResolutionTests = (factory: RefResolverContextFactory) => {
    const filesAST: FilesAST = {
        [path1yaml]: { types: { Type1: {} as any }, imports: [] },
        [path3yaml]: { types: { Type3: {} as any }, imports: [] },
        [path4yaml]: { types: { Type4: {} as any }, imports: [] },
        [path5yaml]: { types: { Type5: {} as any }, imports: [] },
        [lib1yaml]: { types: { LibType: {} as any }, imports: [] },
        [lib2yaml]: { types: { LibType2: {} as any }, imports: [] },
    };

    const strRes = factory({
        filesAST,
        roots: [`${__dirname}/lib1`],
    })(path2yaml);

    // same level
    expect(
        strRes({
            type: ['Type1', undefined],
            link: './1.yaml#/definitions/Type1',
        }),
    ).toBe(path1yaml);
    expect(
        strRes({
            type: ['Type1', undefined],
            link: '1.yaml#/definitions/Type1',
        }),
    ).toBe(path1yaml);

    // child level
    expect(
        strRes({
            type: ['Type3', undefined],
            link: './z/3.yaml#/definitions/Type3',
        }),
    ).toBe(path3yaml);
    expect(
        strRes({
            type: ['Type3', undefined],
            link: 'z/3.yaml#/definitions/Type3',
        }),
    ).toBe(path3yaml);

    // different folder under parent
    expect(
        strRes({
            type: ['Type4', undefined],
            link: '../../a/4.yaml#/definitions/Type4',
        }),
    ).toBe(path4yaml);
    expect(
        strRes({
            type: ['Type4', undefined],
            link: 'a/4.yaml#/definitions/Type4',
        }),
    ).toBe(path4yaml);

    // parent folder
    expect(
        strRes({
            type: ['Type5', undefined],
            link: '../../5.yaml#/definitions/Type5',
        }),
    ).toBe(path5yaml);
    expect(
        strRes({
            type: ['Type5', undefined],
            link: '/5.yaml#/definitions/Type5',
        }),
    ).toBe(path5yaml);

    // no type in file
    expect(
        strRes({
            type: ['TypeX', undefined],
            link: './1.yaml#/definitions/TypeX',
        }),
    ).toBe(undefined);

    // no file
    expect(
        strRes({
            type: ['TypeX', undefined],
            link: '../1.yaml#/definitions/TypeX',
        }),
    ).toBe(undefined);

    // lib
    expect(
        strRes({
            type: ['LibType', undefined],
            link: 'lib1/1.yaml#/definitions/LibType',
        }),
    ).toBe(lib1yaml);
    expect(
        strRes({
            type: ['LibType2', undefined],
            link: 'lib1/docs/yaml/2.yaml#/definitions/LibType2',
        }),
    ).toBe(lib2yaml);
};

describe('utils/yaml/resolution', () => {
    test('localRefResolution', () => {
        const fileName = `${__dirname}/1.yaml`;
        const localRes = localRefResolution({
            filesAST: {
                [fileName]: { types: { Type1: {} as any }, imports: [] },
            },
        })(fileName);

        expect(
            localRes({
                type: ['Type1', undefined],
                link: '#/definitions/Type1',
            }),
        ).toBe(fileName);
        expect(
            localRes({
                type: ['Type2', undefined],
                link: '#/definitions/Type2',
            }),
        ).toBe(undefined);
    });

    test('sortRoots', () => {
        expect(
            sortRoots(
                ['repo/services/libs', 'repo/services/service1/libs', 'repo/services/service1/docs/yaml/common'],
                'repo/services/service1/docs/yaml/api/api.yaml',
            ),
        ).toEqual(['repo/services/service1/docs/yaml/common', 'repo/services/service1/libs', 'repo/services/libs']);
    });

    test('strongRefResolution', async () => {
        strongResolutionTests(strongRefResolution);
    });

    test('docsYamlIgnoreResolution common', () => {
        strongResolutionTests(docsYamlIgnoreResolution);
    });

    test('docsYamlIgnoreResolution cut path', () => {
        const apiyaml = `${__dirname}/service/docs/yaml/api/1.yaml`;
        const defyaml = `${__dirname}/service/docs/yaml/def.yaml`;
        const libyaml = `${__dirname}/libraries/dummy/docs/yaml/def.yaml`;
        const filesAST: FilesAST = {
            [defyaml]: { types: { Type1: {} as any }, imports: [] },
            [libyaml]: { types: { LibType: {} as any }, imports: [] },
        };

        const res = docsYamlIgnoreResolution({
            filesAST,
            roots: [`${__dirname}/libraries`],
        })(apiyaml);

        expect(
            res({
                type: ['Type1', undefined],
                link: 'service/def.yaml#/definitions/Type1',
            }),
        ).toBe(defyaml);
        expect(
            res({
                type: ['LibType', undefined],
                link: 'dummy/def.yaml#/definitions/LibType',
            }),
        ).toBe(libyaml);
    });

    test('sortWeakResolutions', () => {
        expect(
            sortWeakResolutions('repo/services/orders/api/1.yaml', [
                'repo/services/payments/api/1.yaml',
                'repo/services/definitions.yaml',
                'repo/services/orders/definitions.yaml',
                'repo/services/orders/api/common/utils/1.yaml',
                'repo/services/orders/api/common/1.yaml',
                'repo/services/orders/api/2.yaml',
                'repo/services/orders/api/1.yaml',
            ]),
        ).toEqual([
            'repo/services/orders/api/1.yaml',
            'repo/services/orders/api/2.yaml',
            'repo/services/orders/api/common/1.yaml',
            'repo/services/orders/api/common/utils/1.yaml',
            'repo/services/orders/definitions.yaml',
            'repo/services/definitions.yaml',
            'repo/services/payments/api/1.yaml',
        ]);
    });
});
