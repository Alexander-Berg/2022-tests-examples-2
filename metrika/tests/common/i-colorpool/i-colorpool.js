describe('i-colorpool', function () {
    var colorpool;

    beforeEach(function () {
        colorpool = BN('i-colorpool').create();
    });
    afterEach(function () {
        colorpool.destruct();
    });

    it('method getAllColors', function () {
        var allColors = colorpool.getAllColors();

        expect(allColors, 'returns not empty array')
            .to.have.length.gt(1);
    });

    describe('method get', function () {
        it('returns uniq color index', function () {
            var allColors = colorpool.getAllColors(),
                length = allColors.length,
                prevIdx = colorpool.get(),
                uniq = true,
                i = 1,
                idx;

            while (uniq && (i++ < length)) {
                idx = colorpool.get();
                uniq = prevIdx < idx;
            }

            expect(uniq).to.be.equal(true);
        });

        it('returns correct color index in the loop', function () {
            var allColors = colorpool.getAllColors(),
                length = allColors.length,
                a1 = [],
                a2 = [],
                i = 0;

            while (i++ < length) {
                a1.push(colorpool.get());
            }
            i = 0;
            while (i++ < length) {
                a2.push(colorpool.get());
            }

            expect(a1).to.be.eql(a2);
        });

        it('returns correct color index when called with same color index', function () {
            expect(colorpool.get(1))
                .to.be.equal(colorpool.get(1));
        });

        it('returns correct color index when called with uniq color index', function () {
            expect(colorpool.get(1))
                .not.to.equal(colorpool.get(2));
        });

        it('doesn\'t return exclusive color', function () {
            var allColors = colorpool.getAllColors(),
                length = allColors.length,
                exclusiveColorIdx = Math.ceil(length / 2),
                indexes = [];

            exclusiveColorIdx = colorpool.get(exclusiveColorIdx, true);
            while (length--) {
                indexes.push(colorpool.get());
            }

            expect(indexes)
                .not.to.contains(exclusiveColorIdx);
        });

        it('returns freed color index', function () {
            var allColors = colorpool.getAllColors(),
                length = allColors.length,
                freeColorIdx = Math.ceil(length / 2);

            while (length--) {
                colorpool.get();
            }
            colorpool.free(freeColorIdx);
            expect(Number(colorpool.get()))
                .to.be.equal(freeColorIdx);
        });
    });

    describe('method getColor', function () {
        it('returns uniq color on each call', function () {
            var allColors = colorpool.getAllColors(),
                length = allColors.length,
                fetchedColors = [];

            while (length--) {
                fetchedColors.push(colorpool.getColor());
            }
            expect(fetchedColors.every(function (color) {
                return fetchedColors.indexOf(color) === fetchedColors.lastIndexOf(color);
            })).to.be.equal(true);
        });

        it('returns correct color by index when called with same color index', function () {
            expect(colorpool.getColor(1))
                .to.be.equal(colorpool.getColor(1));
        });

        it('returns correct color by index when called with uniq color index', function () {
            expect(colorpool.getColor(1))
                .not.to.equal(colorpool.getColor(2));
        });
    });

    describe('method getColors', function () {
        var minIdx, maxIdx;

        beforeEach(function () {
            var allColors = colorpool.getAllColors(),
                length = allColors.length;
            minIdx = Math.ceil(length / 4);
            maxIdx = Math.ceil(length * 3 / 4);
        });

        it('returns array with correct length', function () {
            expect(colorpool.getColors([minIdx, maxIdx]))
                .to.have.length(2);
        });

        it('returns array with correct items', function () {
            expect(colorpool.getColors([minIdx, maxIdx]))
                .to.be.eql([colorpool.getColor(minIdx), colorpool.getColor(maxIdx)]);
        });

        it('returns empty array when argument is an empty array', function () {
            expect(colorpool.getColors([]))
                .to.have.length(0);
        });
    });

    describe('method getByKeys', function () {
        var keys = ['k1', 'k2', 'k3'];

        it('returns an array with same length as keys', function () {
            expect(colorpool.getByKeys(keys))
                .to.have.length(keys.length);
        });

        it('returns an array with same color indexes for same keys', function () {
            expect(colorpool.getByKeys(keys))
                .to.be.eql(colorpool.getByKeys(keys));
        });

        it('returns an array of uniq indexes', function () {
            var indexes = colorpool.getByKeys(keys);
            expect(indexes.every(function (index) {
                return indexes.indexOf(index) === indexes.lastIndexOf(index);
            }))
                .to.be.equal(true);
        });
    });

    describe('method free', function () {
        it('releases color by index', function () {
            var allColors = colorpool.getAllColors(),
                length = allColors.length,
                freeColorIdx = Math.ceil(length / 2);

            while (length--) {
                colorpool.get();
            }
            colorpool.free(freeColorIdx);
            expect(Number(colorpool.get()))
                .to.be.equal(freeColorIdx);
        });

        it('releases exclusive color by index', function () {
            var allColors = colorpool.getAllColors(),
                length = allColors.length,
                exclusiveColorIdx = Math.ceil(length / 2);

            colorpool.get(exclusiveColorIdx, true);
            while (--length) {
                colorpool.get();
            }
            colorpool.free(exclusiveColorIdx);
            expect(Number(colorpool.get()))
                .to.be.equal(exclusiveColorIdx);
        });
    });

    it('method reset', function () {
        var firstColor = colorpool.getColor();
        colorpool.reset();
        expect(colorpool.getColor(), 'getColor returns first color after reset')
            .to.be.equal(firstColor);
    });
});

