import * as fs from 'fs';
import { PluginItem, transform } from '@babel/core';

jest.mock('fs', () => {
    const fs = jest.requireActual('fs');

    return {
        ...fs,
        readFileSync(path: fs.PathLike | number, options?: { encoding?: null; flag?: string } | null) {
            if (path === '/tests/other.js') {
                return 'doSomething();';
            }
            return fs.readFileSync(path, options);
        },
        existsSync(path: fs.PathLike) {
            const filePath = path.toString();
            if (filePath.startsWith('/levels/common')) {
                return filePath === '/levels/common/block/block.view.tsx';
            }
            return fs.existsSync(path);
        }
    };
});

jest.mock('../../pathsUtils', () => ({
    getPaths() {
        return {
            '@block': [
                '/levels/common'
            ]
        };
    },
    getLevels() {
        return [{
            name: 'commonViews',
            resolvedPath: '/levels/common'
        }];
    }
}));

jest.mock('../../utils/clsCore', function() {
    return {
        CLSCore: class CLSCore {
            full(val: string): string {
                return `full-random-${val}`;
            }
            part(val: string): string {
                return `part-random-${val}`;
            }
        }
    };
});

describe('babelPlugins', () => {
    for (const esModules of [false, true]) {
        describe(`esmodules: ${String(esModules)}`, () => {
            function run(plugin: PluginItem, code: string, filename: string): string {
                const result = transform(code, {
                    filename: '/levels/common/block/' + filename,
                    presets: [
                        [
                            '@babel/preset-env',
                            {
                                targets: {
                                    node: 'current'
                                },
                                // false = keep es modules
                                // auto = transform to node.js common modules
                                modules: esModules ? false : 'auto'
                            }
                        ]
                    ],
                    plugins: [plugin],

                });

                if (!result || !result.code) {
                    throw new Error('Something went wrong');
                }

                return result.code;
            }
            test('appendViewName', () => {
                expect(run([require('../../babel/appendViewName')], `
                    export function B(){}

                    export { B as b };
                `, 'block.view.tsx')).toMatchSnapshot();
            });

            test('includeReplace', () => {
                expect(run([require('../../babel/includeReplace'), { rootDir: '/tests' }], `
                    INCLUDE('other.js');
                `, 'block.view.tsx')).toMatchSnapshot();
            });

            test('pathsBabelPlugin', () => {
                expect(run([require('../../babel/pathsBabelPlugin'), { levelsPath: 'levels.json' }], `
                    import { Block } from '@block/block/block.view';
                `, 'block.view.tsx')).toMatchSnapshot();
            });

            test('replaceTestDepsPlugin', () => {
                expect(run([require('../../babel/replaceTestDepsPlugin'), { levelsPath: 'levels.json' }], `
                    import { execView } from '@lib/views/execView';
                    import { mockView } from '@lib/views/mock';

                    describe('home-logo', function() {
                        it('default', function() {
                            const html = execView('home-logo', {}, mockReq({}, reqs.std));

                            expect(html).toMatchSnapshot();
                        });
                    });
                `, 'block.view.test.tsx')).toMatchSnapshot();
            });

            test('transformViewsUsageRef', () => {
                const plugin = require('../../babel/transformViewsUsageRef');

                expect(run([plugin, { levelsPath: 'levels.json' }], `
                    export function Block(data, req, execView) {
                        return execView(BlockInner);
                    }

                    export function BlockInner() {
                        return 'abc';
                    }
                `, 'block.view.tsx')).toMatchSnapshot();

                expect(run([plugin, { levelsPath: 'levels.json' }], `
                    import cached from '@lib/views/makeCached';

                    export function Root(data, req, execView) {
                        return execView(Block) + execView(Block2) + execView(BlockInner);
                    };

                    export function Block(data, req, execView) {
                        return execView(BlockInner);
                    }
                    Block.isCached = true;

                    export const Block2 = cached(function Block2(data, req, execView) {
                        return execView(BlockInner);
                    });

                    export function BlockInner() {
                        return 'abc';
                    }
                `, 'block.view.tsx')).toMatchSnapshot();
            });

            test('transformViewsUsageString', () => {
                expect(run([require('../../babel/transformViewsUsageString'), { levelsPath: 'levels.json' }], `
                    import { Other } from '../other/other.view';

                    import { Other2 as OtherSecond } from '../other/other.view';

                    import { BlockInner as BlockInnerBase } from '@blockBase/block/block.view';

                    const Something = home.Something;

                    export function Block(data, req, execView) {
                        return execView(BlockInner) + execView(BlockInnerBase) + execView(Other) + execView(OtherSecond) + execView(Something);
                    }

                    export function BlockInner() {
                        return 'abc';
                    }
                `, 'block.view.tsx')).toMatchSnapshot();
            });

            test('replaceBaseViewDef', () => {
                expect(run([require('../../babel/replaceBaseViewDef')], `
                    import { Block as BlockBase, BlockInner as BlockInnerBase } from '@blockBase/block/block.view';

                    export function Block(data, req, execView) {
                        return execView(BlockBase) + execView(BlockInnerBase);
                    }

                    export * from '@blockBase/block/block.view';
                `, 'block.view.tsx')).toMatchSnapshot();
            });

            test('transformCachedDecl', () => {
                let plugin = require('../../babel/transformCachedDecl');

                expect(run([plugin], `
                    export function Block1(arg) {
                        return 'abc';
                    };

                    export function Block2(arg) {
                    };
                    Block2.isCached = true;
                `, 'block.view.tsx')).toMatchSnapshot();

                expect(run([plugin], `
                    export function Block1(arg) {
                        return 'abc';
                    };

                    export function Block2(arg) {
                    };
                `, 'block.view.tsx')).toMatchSnapshot();
            });

            test('clsGenPlugin', () => {
                expect(run([require('../../babel/clsGenPlugin')], `
                    export function Block(data, req, execView) {
                        return req.cls.full('block') + home.cls.part('part');
                    }
                `, 'block.view.tsx')).toMatchSnapshot();
            });
        });
    }
});
