var expect = require('chai').expect;
var Tech = require('../techs/deps-per-block.js');

describe('deps-per-block', function () {
    var t = new Tech();
    t.node = {
        getLogger: function () {
            return {
                getErrorAction: console.error,
                getWarningAction: console.log
            };
        }
    };
    it('bemToId', function () {
        t.bemToId({
            block: 'name'
        }).should.equal('name');
        t.bemToId({
            block: 'name',
            elem: 'elem'
        }).should.equal('name__elem');

        t.bemToId({
            block: 'name',
            mod: 'foo',
            val: 'bar'
        }).should.equal('name_foo_bar');

        t.bemToId({
            block: 'name',
            elem: 'elem',
            mod: 'foo',
            val: 'bar'
        }).should.equal('name__elem_foo_bar');
    });

    describe('normalizeDeps', function () {
        it('блоки', function() {
            expect(t.normalizeDeps({
                block: 'block'
            }, {
                shouldDeps: [
                    'foo',
                    {
                        block: 'bar'
                    },
                    {
                        name: 'baz'
                    }
                ]
            })).to.deep.equal({
                mustDeps: [],
                shouldDeps: [
                    'foo',
                    'bar',
                    'baz'
                ]
            });
        });

        it('элементы', function () {
            expect(t.normalizeDeps({
                block: 'block'
            }, {
                shouldDeps: [
                    {
                        block: 'foo',
                        elem: 'bar'
                    },
                    {
                        block: 'foo',
                        elem: ['qwe']
                    },
                    {
                        block: 'baz',
                        elems: ['qwer', 'tyu']
                    }
                ]
            })).to.deep.equal({
                mustDeps: [],
                shouldDeps: [
                    'foo__bar',
                    'foo__qwe',
                    'baz',
                    'baz__qwer',
                    'baz__tyu'
                ]
            });
        });

        it('модификаторы', function () {
            expect(t.normalizeDeps({
                block: 'block'
            }, {
                shouldDeps: [
                    {
                        block: 'foo',
                        mod: 'bar',
                        val: 'baz'
                    },
                    {
                        block: 'baz',
                        mods: {
                            foo: 'bar',
                            bar: 'foo',
                            qwe: ['rty', 'uio']
                        }
                    },
                    {
                        block: 'qwe',
                        mods: [
                            {
                                name: 'rty',
                                val: 'uio'
                            },
                            {
                                name: 'pas',
                                vals: ['dfg', 'ghj']
                            }
                        ]
                    }
                ]
            })).to.deep.equal({
                mustDeps: [],
                shouldDeps: [
                    'foo_bar_baz',
                    'baz',
                    'baz_foo',
                    'baz_foo_bar',
                    'baz_bar',
                    'baz_bar_foo',
                    'baz_qwe',
                    'baz_qwe_rty',
                    'baz_qwe_uio',
                    'qwe',
                    'qwe_rty_uio',
                    'qwe_pas',
                    'qwe_pas_dfg',
                    'qwe_pas_ghj'
                ]
            });
        });

        it('элементы с модификаторами', function () {
            expect(t.normalizeDeps({
                block: 'block'
            }, {
                shouldDeps: [
                    {
                        block: 'foo',
                        elem: 'bar',
                        mod: 'baz',
                        val: 'qwe'
                    },
                    {
                        block: 'zxc',
                        elems: [
                            {
                                elem: 'cvb',
                                mods: {
                                    asd: 'fgh'
                                }
                            },
                            {
                                elem: 'nm',
                                mods: {
                                    fgh: 'asd'
                                }
                            }
                        ]
                    }

                ]
            })).to.deep.equal({
                mustDeps: [],
                shouldDeps: [
                    'foo__bar_baz_qwe',
                    'zxc',
                    'zxc__cvb',
                    'zxc__cvb_asd',
                    'zxc__cvb_asd_fgh',
                    'zxc__nm',
                    'zxc__nm_fgh',
                    'zxc__nm_fgh_asd'
                ]
            });
        });

        it('неявное указание блока', function () {
            expect(t.normalizeDeps({
                block: 'block'
            }, {
                shouldDeps: [
                    {
                        elem: 'bar'
                    },
                    {
                        mods: {
                            foo: 'bar'
                        }
                    }
                ]
            })).to.deep.equal({
                mustDeps: [],
                shouldDeps: [
                    'block__bar',
                    'block_foo',
                    'block_foo_bar'
                ]
            });

            expect(t.normalizeDeps({
                block: 'block',
                elem: 'elem'
            }, {
                shouldDeps: [
                    {
                        elem: 'bar'
                    },
                    {
                        elems: ['asd', 'fgh']
                    },
                    {
                        mods: {
                            foo: 'bar'
                        }
                    },
                    {
                        block: 'foo',
                        mods: {
                            bar: 'baz'
                        }
                    }
                ]
            })).to.deep.equal({
                mustDeps: [],
                shouldDeps: [
                    'block__bar',
                    'block__asd',
                    'block__fgh',
                    'block__elem_foo',
                    'block__elem_foo_bar',
                    'foo',
                    'foo_bar',
                    'foo_bar_baz'
                ]
            });

            expect(t.normalizeDeps({
                block: 'block',
                mod: 'mod',
                val: 'val'
            }, {
                shouldDeps: [
                    {
                        elem: 'bar'
                    },
                    {
                        mods: {
                            foo: 'baz'
                        }
                    }
                ]
            })).to.deep.equal({
                mustDeps: [],
                shouldDeps: [
                    'block__bar',
                    'block_foo',
                    'block_foo_baz'
                ]
            });
        });
    });
});