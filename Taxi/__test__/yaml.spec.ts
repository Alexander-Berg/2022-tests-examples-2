import path from 'path';

import { formatContent } from '../..';
import { CliOptions, FullConfig, TypesMap } from '../../../types';
import { proxyPaths } from '../../common';
import { createDebugContext } from '../../debug';
import { StrictError } from '../../errors';
import { createPluginComposite } from '../../plugins';
import {
    getSpecsList,
    getTypeNameFromRef,
    isOpenApi2,
    isOpenApi3,
    isValidType,
    parseSpec,
    processYaml as processYamlOrig,
} from '../../yaml';

const TYPES_MAP: TypesMap = {
    double: 'number',
    integer: 'number',
    float: 'number',
    list: 'array',
    data: 'object',
};

const CLI_OPTIONS: CliOptions = {
    context: __dirname,
    config: '',
    noCheckout: true,
};

const FULL_CONFIG: FullConfig = {
    ...CLI_OPTIONS,
    specsDir: './specs',
    typingsDir: './typings',
    scope: undefined,
    plugins: createPluginComposite([]),
    repositories: [
        {
            vcs: 'git',
            name: 'test',
            url: '',
            branch: '',
            checkout: [''],
            targets: {
                test: [''],
            },
        },
    ],
};

const REPO_ROOT = `${__dirname}/specs`;

type OriginalOptions = Parameters<typeof processYamlOrig>[0]
type NoPluginsOptions = Omit<OriginalOptions, 'plugins'>

const processYaml = (options: NoPluginsOptions) => {
    return processYamlOrig({ plugins: createPluginComposite([]), ...options });
};

describe('utils/yaml', () => {
    test('parseSpec', async () => {
        const filePath = path.join(__dirname, 'specs/api/1.yaml');
        const obj = await parseSpec(filePath);

        expect(obj?.swagger).toBe('2.0');
    });

    test('getSpecsList', async () => {
        const folderPath = path.join(__dirname, 'specs/api');
        const files = await getSpecsList(folderPath);

        expect(files.map(file => file.replace(folderPath, ''))).toEqual(['/1.yaml', '/2.yaml', '/subfolder/3.yaml']);
    });

    test('getTypeNameFromRef', () => {
        expect(getTypeNameFromRef('admin-orders/definitions.yaml#/definitions/BadStatus')).toBe('BadStatus');
    });

    test('getOpenApiVersion', () => {
        expect(isOpenApi3({ swagger: '2.0' })).toBe(false);
        expect(isOpenApi3({ definitions: {} })).toBe(false);
        expect(isOpenApi3({ swagger: '3.0' })).toBe(false);
        expect(isOpenApi3({})).toBe(false);

        expect(isOpenApi3({ openapi: '3.0.0' })).toBe(true);
        expect(isOpenApi3({ components: { schemas: {} } })).toBe(true);

        expect(isOpenApi2({ swagger: '2.0' })).toBe(true);
        expect(isOpenApi2({ definitions: {} })).toBe(true);
        expect(isOpenApi2({ swagger: '3.0' })).toBe(true);

        expect(isOpenApi2({})).toBe(false);
        expect(isOpenApi2({ openapi: '3.0.0' })).toBe(false);
        expect(isOpenApi2({ components: { schemas: {} } })).toBe(false);
    });

    test('isValidType', () => {
        expect(isValidType(proxyPaths({ type: 'boolean' as const }))).toBe(true);
        expect(isValidType(proxyPaths({ type: ['boolean' as const] }))).toBe(true);
        expect(isValidType(proxyPaths({ type: undefined }))).toBe(true);
        expect(isValidType(proxyPaths({ type: null }))).toBe(true);

        expect(isValidType(proxyPaths({ type: {} as any }))).toBe(false);
        expect(isValidType(proxyPaths({ type: 2 as any }))).toBe(false);
        expect(isValidType(proxyPaths({ type: true as any }))).toBe(false);
    });

    test('plain type', async () => {
        const filePath = path.join(__dirname, 'specs/plain-type.yaml');
        const result = await processYaml({ targetsList: { test: [filePath] }, roots: [REPO_ROOT] });

        expect(formatContent(result[filePath])).toBe(
            formatContent(`
            export type PlainType = string;
            export type StringEnum = 'x' | 'y';
            export type NumberEnum = 1 | 2;
        `),
        );
    });

    test('plain object', async () => {
        const filePath = path.join(__dirname, 'specs/plain-object.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath] },
                    typesMap: TYPES_MAP,
                    roots: [REPO_ROOT],
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            /**
            * xxxx
            * */
            export type PlainObject = {
                /**
                * xxxx
                * yyyy
                * */
                a: number;
                /**
                * xxxx
                * */
                b?: string;
                c?: boolean;
                d?: number;
                e: number;
            }
        `),
        );
    });

    test('plain array', async () => {
        const filePath = path.join(__dirname, 'specs/plain-array.yaml');
        const result = await processYaml({ targetsList: { test: [filePath] }, roots: [REPO_ROOT] });

        expect(result[filePath]?.trim()).toBe('export type PlainArray = string[];');
    });

    test('array with no items definition', async () => {
        const filePath = path.join(__dirname, 'specs/array-no-items.yaml');
        const result = await processYaml({ targetsList: { test: [filePath] }, roots: [REPO_ROOT] });

        expect(result[filePath]?.trim()).toBe('export type UnknownArray = unknown[];');
    });

    test('one of', async () => {
        const filePath = path.join(__dirname, 'specs/one-of.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath] },
                    typesMap: TYPES_MAP,
                    roots: [REPO_ROOT],
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type OneOfType = string | {
                a: number;
                b?: string;
                c?: boolean;
                d?: number;
                e: number;
            }
        `),
        );
    });

    test('one of array', async () => {
        const filePath = path.join(__dirname, 'specs/one-of-array.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath] },
                    typesMap: TYPES_MAP,
                    roots: [REPO_ROOT],
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type OneOfArray = Array<
                string | {
                    a: number;
                    b?: string;
                    c?: boolean;
                    d?: number;
                    e: number;
                }
            >
        `),
        );
    });

    test('all of', async () => {
        const filePath = path.join(__dirname, 'specs/all-of.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath] },
                    typesMap: TYPES_MAP,
                    roots: [REPO_ROOT],
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type AllOfType = string & {
                a: number;
                b?: string;
                c?: boolean;
                d?: number;
                e: number;
            }
        `),
        );
    });

    test('all of array', async () => {
        const filePath = path.join(__dirname, 'specs/all-of-array.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath] },
                    typesMap: TYPES_MAP,
                    roots: [REPO_ROOT],
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type AllOfArray = Array<
                string & {
                    a: number;
                    b?: string;
                    c?: boolean;
                    d?: number;
                    e: number;
                }
            >
        `),
        );
    });

    test('additionalProperties true', async () => {
        const filePath = path.join(__dirname, 'specs/add-props-true.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath] },
                    typesMap: TYPES_MAP,
                    roots: [REPO_ROOT],
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type IndexedObject = {
                [x: string]: any;
            } & {
                a: number;
                b?: string;
                c?: boolean;
                d?: number;
                e: number;
            }
        `),
        );
    });

    test('additionalProperties false', async () => {
        const filePath = path.join(__dirname, 'specs/add-props-false.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath] },
                    typesMap: TYPES_MAP,
                    roots: [REPO_ROOT],
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type PlainObject = {
                a: number;
                b?: string;
                c?: boolean;
                d?: number;
                e: number;
            }
        `),
        );
    });

    test('additionalProperties object', async () => {
        const filePath = path.join(__dirname, 'specs/add-props-obj.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath] },
                    typesMap: TYPES_MAP,
                    roots: [REPO_ROOT],
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type UnionObject = {
                [x: string]: {
                    x?: number;
                }
            } & {
                a: number;
                b?: string;
                c?: boolean;
                d?: number;
                e: number;
            }
        `),
        );
    });

    test('oneOf with additionalProperties', async () => {
        const filePath = path.join(__dirname, 'specs/one-of-add-props.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath] },
                    typesMap: TYPES_MAP,
                    roots: [REPO_ROOT],
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type OneOfType = string | {
                [x: string]: {
                    x?: number;
                }
            } & {
                a: number;
                b?: string;
                c?: boolean;
                d?: number;
                e: number;
            }
        `),
        );
    });

    test('oneOf and properties', async () => {
        const filePath = path.join(__dirname, 'specs/one-of-obj.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath] },
                    typesMap: TYPES_MAP,
                    roots: [REPO_ROOT],
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type CombinedType = {
                x: number;
            } & (
                | ({
                    [x: string]: {
                        c?: boolean;
                    }
                } & {
                    a: number;
                })
                | ({
                    [x: string]: any;
                } & {
                    e: number;
                })
            )
        `),
        );
    });

    test('oneOf and allOf', async () => {
        const filePath = path.join(__dirname, 'specs/one-of-all-of.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath] },
                    typesMap: TYPES_MAP,
                    roots: [REPO_ROOT],
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type CombinedType = boolean & {
                x: number;
            } & (
                | string
                | {
                    a: number;
                    b?: string;
                    c?: boolean;
                    d?: number;
                    e: number;
                }
            )
        `),
        );
    });

    test('local ref unknown', async () => {
        const filePath = path.join(__dirname, 'specs/local-ref-unknown.yaml');
        const result = formatContent(
            (await processYaml({ targetsList: { test: [filePath] }, roots: [REPO_ROOT] }))[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type Type1 = {
                x?: Type2;
            };
            export type Type2 = unknown;
        `),
        );
    });

    test('local ref', async () => {
        const filePath = path.join(__dirname, 'specs/local-ref.yaml');
        const result = formatContent(
            (await processYaml({ targetsList: { test: [filePath] }, roots: [REPO_ROOT] }))[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type Type1 = ({
                [x: string]: {
                    y: string;
                } | Type3
            }) & {
                x?: Type2;
            };
            export type Type2 = string;
            export type Type3 = Type4;
            export type Type4 = boolean;
        `),
        );
    });

    test('open api 3', async () => {
        const filePath = path.join(__dirname, 'specs/openapi-3.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath] },
                    typesMap: TYPES_MAP,
                    roots: [REPO_ROOT],
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type PlainObject = {
                a: number;
                b?: string;
                c?: boolean;
                d?: number;
                e: number;
            }
        `),
        );
    });

    test('no types', async () => {
        const filePath = path.join(__dirname, 'specs/no-types.yaml');
        const result = await processYaml({ targetsList: { test: [filePath] }, roots: [REPO_ROOT] });

        expect(result[filePath]).toBe(undefined);
    });

    test('refs to other files', async () => {
        const folderPath = path.join(__dirname, 'specs/api');
        const fileNames = await getSpecsList(folderPath);

        const result = await processYaml({
            targetsList: { test: fileNames },
            roots: [REPO_ROOT],
            useShortPaths: false,
        });

        // src/utils/__test__/specs/api/1.yaml
        expect(formatContent(result[fileNames[0]])).toBe(
            formatContent(`
            export type Type1 = boolean;
        `),
        );

        // src/utils/__test__/specs/api/2.yaml
        expect(formatContent(result[fileNames[1]])).toBe(
            formatContent(`
            import { Type1 } from './1';
            export type Type2 = string | Type1;
            export type Type21 = Type1;
            export type Type25 = boolean;
        `),
        );

        // src/utils/__test__/specs/api/subfolder/3.yaml
        expect(formatContent(result[fileNames[2]])).toBe(
            formatContent(`
            import { Type2 } from '../2';
            export type Type3 = Type2 | Type25;
            export type Type25 = boolean;
        `),
        );
    });

    test('null', async () => {
        const filePath = path.join(__dirname, 'specs/null.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath] },
                    typesMap: TYPES_MAP,
                    roots: [REPO_ROOT],
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type PlainObject = {
                a?: number | null;
                b?: null;
                c?: null;
                d?: number | null;
                e?: number | null;
            }
        `),
        );
    });

    test('multitype', async () => {
        const filePath = path.join(__dirname, 'specs/multitype.yaml');
        const result = formatContent(
            (await processYaml({ targetsList: { test: [filePath] }, roots: [REPO_ROOT] }))[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type MultiType = number | string | null;
        `),
        );
    });

    test('invalid names', async () => {
        const filePath = path.join(__dirname, 'specs/invalid-names.yaml');
        const result = formatContent(
            (await processYaml({ targetsList: { test: [filePath] }, roots: [REPO_ROOT] }))[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type _0PlainObject_v1 = string;
            export type _0PlainObject_v2 = {
                "0"?: _0PlainObject_v1;
                "a-2"?: number;
                "2a"?: number;
            }
        `),
        );
    });

    test('unexpected types', async () => {
        const filePath = path.join(__dirname, 'specs/unexpected-types.yaml');
        const debugContext = createDebugContext(FULL_CONFIG, FULL_CONFIG.repositories[0]);
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test1: [filePath], test2: [filePath] },
                    debugContext,
                    roots: [REPO_ROOT],
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type Type1 = unknown;
            export type Type2 = {
                a?: unknown;
                b?: unknown[] | null;
            }
        `),
        );

        expect(debugContext.getInfo().types.unknown).toEqual({
            ['./src/utils/yaml/__test__/specs/unexpected-types.yaml']: [
                'Type1',
                'Type2.properties.a',
                'Type2.properties.b.oneOf.0.type.0.items',
            ],
        });
    });

    test('roots', async () => {
        const filePath = path.join(__dirname, 'specs/repo/service1/docs/yaml/with-lib.yaml');
        const libPath1 = path.join(__dirname, 'specs/libs/lib1/common.yaml');
        const libPath2 = path.join(__dirname, 'specs/libs/lib2/common.yaml');
        const libPath3 = path.join(__dirname, 'specs/repo/service1/libs/lib1/common.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath, libPath1, libPath2, libPath3] },
                    roots: [REPO_ROOT, `${REPO_ROOT}/libs`, `${REPO_ROOT}/repo/service1/libs`],
                    useShortPaths: false,
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            import {CommonType as CommonType_1} from '../../libs/lib1/common';
            import {CommonType as CommonType_2} from '../../../../libs/lib2/common';
            export type PlainObject = CommonType_1 | CommonType_2;
        `),
        );
    });

    test('any of', async () => {
        const filePath = path.join(__dirname, 'specs/any-of.yaml');
        const result = formatContent(
            (await processYaml({ targetsList: { test: [filePath] }, roots: [REPO_ROOT] }))[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type Type1 = string | boolean;
            export type Type2 = string | {
                [x: string]: any;
            };
            export type Type3 = Partial<{
                a?: string;
            } & {
                b?: string;
            }>
        `),
        );
    });

    test('nonstandart types', async () => {
        const filePath = path.join(__dirname, 'specs/nonstandart-types.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath] },
                    typesMap: TYPES_MAP,
                    roots: [REPO_ROOT],
                })
            )[filePath],
        );

        console.log(result);

        expect(result).toBe(
            formatContent(`
            export type Type1 = number[] | {
                a?: number
            }
        `),
        );
    });

    test('empty object', async () => {
        const filePath = path.join(__dirname, 'specs/empty-object.yaml');
        const result = formatContent(
            (await processYaml({ targetsList: { test: [filePath] }, roots: [REPO_ROOT] }))[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type EmptyObject = {
                [x: string]: any;
            };
        `),
        );
    });

    test('same type', async () => {
        const filePath = path.join(__dirname, 'specs/same-type.yaml');
        const result = formatContent(
            (await processYaml({ targetsList: { test: [filePath] }, roots: [REPO_ROOT] }))[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type UnionType = {
                [x: string]: any;
            } | string | null;
            export type IntersectionType = {
                [x: string]: any;
            } & string & null;
        `),
        );
    });

    test('same imports', async () => {
        const filePath = path.join(__dirname, 'specs/same-imports.yaml');
        const lib1Path = path.join(__dirname, 'specs/libs/lib1/common.yaml');
        const lib2Path = path.join(__dirname, 'specs/libs/lib2/common.yaml');

        let result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath, lib1Path, lib2Path] },
                    roots: [REPO_ROOT, `${REPO_ROOT}/libs`],
                    useShortPaths: false,
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            import { CommonType as CommonType_1 } from './libs/lib1/common'
            import { CommonType as CommonType_2 } from './libs/lib2/common'
            export type PlainObject = CommonType_1 | CommonType_2;
        `),
        );

        result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath] },
                    roots: [REPO_ROOT],
                    useShortPaths: false,
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            export type PlainObject = CommonType_1 | CommonType_2;
            export type CommonType_1 = unknown;
            export type CommonType_2 = unknown;
        `),
        );

        result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath, lib1Path] },
                    roots: [REPO_ROOT, `${__dirname}/specs/libs`],
                    useWeakResolution: false,
                    useShortPaths: false,
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            import { CommonType as CommonType_1 } from './libs/lib1/common'
            export type PlainObject = CommonType_1 | CommonType_2;
            export type CommonType_2 = unknown;
        `),
        );
    });

    test('reduced ref', async () => {
        const filePath = path.join(__dirname, 'specs/reduced-ref.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: {
                        test: [
                            filePath,
                            path.join(__dirname, 'specs/repo/service1/docs/yaml/api/api.yaml'),
                            path.join(__dirname, 'specs/repo/service1/docs/yaml/definitions.yaml'),
                            path.join(__dirname, 'specs/repo/service2/docs/yaml/definitions.yaml'),
                        ],
                    },
                    roots: [REPO_ROOT],
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            import {CommonType as CommonType_1} from './repo/service1/definitions';
            import {CommonType as CommonType_2} from './repo/service2/definitions';
            export type Type1 = CommonType_1 | CommonType_2;
        `),
        );
    });

    test('reduced ref partial', async () => {
        const filePath = path.join(__dirname, 'specs/reduced-ref.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: {
                        service1: [
                            filePath,
                            path.join(__dirname, 'specs/repo/service1/docs/yaml/api/api.yaml'),
                            path.join(__dirname, 'specs/repo/service1/docs/yaml/definitions.yaml'),
                        ],
                        service2: [path.join(__dirname, 'specs/repo/service2/docs/yaml/definitions.yaml')],
                    },
                    roots: [REPO_ROOT],
                    useWeakResolution: false,
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            import { CommonType as CommonType_1 } from './repo/service1/definitions';
            export type Type1 = CommonType_1 | CommonType_2;
            export type CommonType_2 = unknown;
        `),
        );
    });

    test('reduced ref with scope', async () => {
        const filePath = path.join(__dirname, 'specs/reduced-ref.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: {
                        service1: [
                            filePath,
                            path.join(__dirname, 'specs/repo/service1/docs/yaml/api/api.yaml'),
                            path.join(__dirname, 'specs/repo/service1/docs/yaml/definitions.yaml'),
                        ],
                        service2: [path.join(__dirname, 'specs/repo/service2/docs/yaml/definitions.yaml')],
                    },
                    scope: ['service1'],
                    roots: [REPO_ROOT],
                    useWeakResolution: false,
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            import { CommonType as CommonType_1 } from './repo/service1/definitions';
            export type Type1 = CommonType_1 | CommonType_2;
            export type CommonType_2 = unknown;
        `),
        );
    });

    test('ref conflict with local type', async () => {
        const filePath = path.join(__dirname, 'specs/type-ref-conflict.yaml');
        const libPath1 = path.join(__dirname, 'specs/libs/lib1/common.yaml');
        const result = formatContent(
            (
                await processYaml({
                    targetsList: { test: [filePath, libPath1] },
                    roots: [REPO_ROOT],
                    useShortPaths: false,
                })
            )[filePath],
        );

        expect(result).toBe(
            formatContent(`
            import {CommonType as CommonType_1, CommonResponse as CommonResponse_1} from './libs/lib1/common';
            export type CommonType = string;
            export type CommonResponse = number;
            export type PlainObject = {
                a?: CommonType_1;
                b?: CommonType;
                c?: CommonResponse_1;
                d?: CommonResponse_1;
            }
        `),
        );
    });

    test('strict unknown types', async () => {
        const filePath = path.join(__dirname, 'specs/unexpected-types.yaml');
        const debugContext = createDebugContext(FULL_CONFIG, FULL_CONFIG.repositories[0]);
        const result = await processYaml({
            targetsList: { test1: [filePath] },
            debugContext,
            roots: [REPO_ROOT],
            strict: true,
        }).catch(err => err);

        expect(result instanceof StrictError).toBe(true);

        expect(debugContext.getInfo().types.unknown).toEqual({
            ['./src/utils/yaml/__test__/specs/unexpected-types.yaml']: [
                'Type1',
                'Type2.properties.a',
                'Type2.properties.b.oneOf.0.type.0.items',
            ],
        });
    });

    test('strict unknown refs', async () => {
        const filePath = path.join(__dirname, 'specs/local-ref-unknown.yaml');
        const debugContext = createDebugContext(FULL_CONFIG, FULL_CONFIG.repositories[0]);
        const result = await processYaml({
            targetsList: { test: [filePath] },
            roots: [REPO_ROOT],
            debugContext,
            strict: true,
        }).catch(err => err);

        expect(result instanceof StrictError).toBe(true);

        expect(debugContext.getInfo().refs.unknown).toEqual({
            ['./src/utils/yaml/__test__/specs/local-ref-unknown.yaml']: [
                {
                    link: '#/definitions/Type2',
                    resolution: '',
                },
            ],
        });
    });
});
