import { DepsTree } from '../depsTree';

describe('home.depsTree', function() {
    describe('resolveDeps', function() {
        test('возвращает всё цепочку зависимостей', function() {
            let tree = new DepsTree({
                a: {
                    shouldDeps: ['b', 'c']
                },
                b: {
                    mustDeps: ['d', 'e']
                },
                c: {
                    shouldDeps: ['d', 'f']
                }
            }, {});

            expect(tree._resolveDeps('a')).toEqual(['a', 'd', 'e', 'b', 'c', 'f']);
        });

        test('исключает выданные ранее блоки', function() {
            let tree = new DepsTree({
                a: {
                    shouldDeps: ['b', 'c']
                },
                b: {
                    mustDeps: ['d', 'e']
                },
                c: {
                    shouldDeps: ['d', 'f']
                }
            }, {});

            expect(tree._resolveDeps('b')).toEqual(['d', 'e', 'b']);

            expect(tree._resolveDeps('b')).toEqual([]);

            expect(tree._resolveDeps('c')).toEqual(['c', 'f']);

            expect(tree._resolveDeps('a')).toEqual(['a']);
        });

        it.skip('A -must-> B -should-> C -must-> A', function() {
            const tree = new DepsTree({
                a: {
                    mustDeps: ['b']
                },
                b: {
                    shouldDeps: ['c']
                },
                c: {
                    mustDeps: ['a']
                }
            }, {});
            expect(tree._resolveDeps('a')).toEqual(['b', 'a', 'c']);
        });

        test('не изменяет объекты, переданные в параметрах', function() {
            let deps = {
                a: {
                    shouldDeps: ['b', 'c']
                },
                b: {
                    mustDeps: ['d', 'e']
                },
                c: {
                    shouldDeps: ['d', 'f']
                }
            };
            let depsStr = JSON.stringify(deps, null, '  ');
            let res = {
                a: '/* a */',
                b: '/* b */',
                c: '/* c */',
                d: '/* d */',
                e: '/* e */',
                f: '/* f */'
            };
            let resStr = JSON.stringify(res, null, '  ');
            let tree = new DepsTree(deps, res);

            expect(tree.get('a')).toEqual('/* a *//* d *//* e *//* b *//* c *//* f */');

            expect(JSON.stringify(deps, null, '  ')).toEqual(depsStr);
            expect(JSON.stringify(res, null, '  ')).toEqual(resStr);
        });
    });

    describe('_resolveIntersection', () => {
        it('возвращает пустое пересечение для одного блока', () => {
            let tree = new DepsTree({
                a: {
                    shouldDeps: ['b', 'c']
                },
                b: {
                    mustDeps: ['d', 'e']
                },
                c: {
                    shouldDeps: ['d', 'f']
                }
            }, {});
            expect(tree._resolveIntersection([['b']])).toEqual([]);
        });

        describe('пересечения между исходными элементами', () => {
            it('возвращает пересечение с исходным элементом', () => {
                let tree = new DepsTree({
                    a: {
                        shouldDeps: ['b', 'c']
                    },
                    b: {
                        mustDeps: ['d', 'e']
                    },
                    c: {
                        shouldDeps: ['d', 'f']
                    }
                }, {});

                expect(tree._resolveIntersection([['a'], ['b']])).toEqual(['b']);
            });

            it('пересечение между исходными списками', () => {
                let tree = new DepsTree({}, {});

                expect(tree._resolveIntersection([['a', 'b', 'x'], ['c', 'x'], ['e', 'b']])).toEqual(['x', 'b']);
            });

            it('повторение элементов в пределах одного списка игнорируются', () => {
                let tree = new DepsTree({}, {});

                expect(tree._resolveIntersection([['a', 'b', 'b', 'x'], ['c', 'x']])).toEqual(['x']);
            });

            it('возвращает только пересечения разных списков, а не зависимостей в пределах одного списка (1 элемент)', () => {
                let tree = new DepsTree({
                    a: {
                        shouldDeps: ['c', 'x', 'd']
                    },
                    b: {
                        shouldDeps: ['x']
                    },
                    c: {
                        shouldDeps: ['e']
                    },
                    d: {
                        shouldDeps: ['e']
                    }
                }, {});
                expect(tree._resolveIntersection([['a'], ['b']])).toEqual(['x']);
            });

            it('возвращает только пересечения разных списков, а не зависимостей в пределах одного списка (несколько элементов)', () => {
                let tree = new DepsTree({
                    a: {
                        shouldDeps: ['c', 'x']
                    },
                    b: {
                        shouldDeps: ['x']
                    },
                    c: {
                        shouldDeps: ['e']
                    },
                    d: {
                        shouldDeps: ['e']
                    }
                }, {});
                expect(tree._resolveIntersection([['a', 'c'], ['b']])).toEqual(['x']);
            });
        });

        it('останавливается на первом уровне пересечения', () => {
            let tree = new DepsTree({
                a: {
                    shouldDeps: ['b', 'c']
                },
                b: {
                    mustDeps: ['d', 'e']
                },
                c: {
                    shouldDeps: ['d', 'f']
                },
                d: {
                    shouldDeps: ['x']
                }
            }, {});

            expect(tree._resolveIntersection([['b'], ['c']])).toEqual(['d']);
        });

        it('возвращает пересечение с разных уровней вложенности', () => {
            let tree = new DepsTree({
                a: {
                    shouldDeps: ['b', 'q']
                },
                b: {
                    mustDeps: ['d', 'e']
                },
                c: {
                    shouldDeps: ['z', 'f']
                },
                d: {
                    shouldDeps: ['x']
                },
                e: {
                    shouldDeps: ['f']
                }
            }, {});

            expect(tree._resolveIntersection([['a'], ['c']])).toEqual(['f']);
        });

        it('возвращает пересечение', () => {
            let tree = new DepsTree({
                a: {
                    shouldDeps: ['e', 'qx', 'q', 'd']
                },
                b: {
                    shouldDeps: ['x', 'qx', 'q', 's']
                },
                d: {
                    shouldDeps: ['z', 'zx', 'k']
                },
                s: {
                    shouldDeps: ['z', 'zx', 'lx']
                },

                c: {
                    shouldDeps: ['zx', 'k']
                },
                sx: {
                    shouldDeps: ['lx']
                }

            }, {});

            expect(tree._resolveIntersection([['a'], ['b']])).toEqual(['qx', 'q', 'z', 'zx']);
        });

        it('исключает использованые зависимости', () => {
            let tree = new DepsTree({
                a: {
                    shouldDeps: ['e', 'qx', 'q', 'd']
                },
                b: {
                    shouldDeps: ['x', 'qx', 'q', 's']
                },
                d: {
                    shouldDeps: ['z', 'zx', 'k']
                },
                s: {
                    shouldDeps: ['z', 'zx', 'lx']
                },

                c: {
                    shouldDeps: ['zx', 'k']
                },
                sx: {
                    shouldDeps: ['lx']
                }

            }, {});

            tree.get(['c', 'qx', 'sx']);

            expect(tree._resolveIntersection([['a'], ['b']])).toEqual(['q', 'z']);
        });
    });
});
