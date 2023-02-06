var expect = require('chai').expect;
var Tech = require('../techs/clean-deps-per-block.js');

describe('clean-deps-per-block', function () {
    var t = new Tech();
    t.node = {
        getLogger: function () {
            return {
                logAction: console.log,
                getErrorAction: console.error,
                getWarningAction: console.log
            };
        }
    };

    it('оставляет блоки со стиями', function () {
        expect(t.process({
            a: {
                shouldDeps: [],
                mustDeps: []
            }
        }, {
            a: 'style'
        })).to.deep.equal({
            a: {
                shouldDeps: [],
                mustDeps: []
            }
        });
    });


    it('выкидывает блоки без стилей и зависимостей', function () {
        expect(t.process({
            a: {
                shouldDeps: [],
                mustDeps: []
            }
        }, {})).to.deep.equal({});
    });

    it('оставляет блоки, зависящие от блоков со стилями', function () {
        expect(t.process({
            a: {
                shouldDeps: ['c'],
                mustDeps: []
            },
            b: {
                shouldDeps: [],
                mustDeps: ['c']
            },
            c: {
                shouldDeps: [],
                mustDeps: []
            }
        }, {
            c: 'style'
        })).to.deep.equal({
            a: {
                shouldDeps: ['c'],
                mustDeps: []
            },
            b: {
                shouldDeps: [],
                mustDeps: ['c']
            },
            c: {
                shouldDeps: [],
                mustDeps: []
            }
        });
    });

    it('выкидывает блоки без стилей, зависящие от выкинутых блоков', function () {
        expect(t.process({
            a: {
                shouldDeps: ['c'],
                mustDeps: []
            },
            b: {
                shouldDeps: [],
                mustDeps: ['c']
            },
            c: {
                shouldDeps: [],
                mustDeps: []
            }
        }, {})).to.deep.equal({});
    });

    it('выкидывает блоки без стилей, неявно зависящие от только выкинутых блоков', function () {
        expect(t.process({
            a: {
                shouldDeps: ['c'],
                mustDeps: []
            },
            b: {
                shouldDeps: [],
                mustDeps: ['c']
            },
            c: {
                shouldDeps: ['e'],
                mustDeps: []
            },
            e: {
                shouldDeps: [],
                mustDeps: []
            }
        }, {})).to.deep.equal({});
    });

    it('выкидывает блоки без стилей, неявно зависящие от блоков со стилями', function () {
        expect(t.process({
            a: {
                shouldDeps: ['c'],
                mustDeps: []
            },
            b: {
                shouldDeps: [],
                mustDeps: ['c']
            },
            c: {
                shouldDeps: ['e'],
                mustDeps: []
            },
            e: {
                shouldDeps: [],
                mustDeps: []
            }
        }, {
            e: 'style'
        })).to.deep.equal({
            a: {
                shouldDeps: ['c'],
                mustDeps: []
            },
            b: {
                shouldDeps: [],
                mustDeps: ['c']
            },
            c: {
                shouldDeps: ['e'],
                mustDeps: []
            },
            e: {
                shouldDeps: [],
                mustDeps: []
            }
        });
    });

    it('оставляет блоки без стилей, у которых есть хотя бы одна зависимость со стилями', function () {
        expect(t.process({
            a: {
                shouldDeps: ['b', 'c'],
                mustDeps: []
            },
            b: {
                shouldDeps: [],
                mustDeps: ['d']
            },
            c: {
                shouldDeps: [],
                mustDeps: ['e']
            },
            d: {
                shouldDeps: [],
                mustDeps: []
            },
            e: {
                shouldDeps: [],
                mustDeps: []
            }
        }, {
            e: 'style'
        })).to.deep.equal({
            a: {
                shouldDeps: ['c'],
                mustDeps: []
            },
            c: {
                shouldDeps: [],
                mustDeps: ['e']
            },
            e: {
                shouldDeps: [],
                mustDeps: []
            }
        });
    });
});