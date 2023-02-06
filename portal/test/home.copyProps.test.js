/* eslint no-unused-expressions: 0 */

describe('home.copyProps', function () {
    it('should copy simple value', function () {
        home.copyProps('str', 1).should.deep.equal('str');
        home.copyProps(123, 1).should.deep.equal(123);
        home.copyProps(true, 1).should.deep.equal(true);
    });

    it('should copy array', function () {
        home.copyProps(['str', 'baz'], [1]).should.deep.equal(['str', 'baz']);
        home.copyProps([123, 'baz'], [1]).should.deep.equal([123, 'baz']);
    });

    it('should copy object', function () {
        home.copyProps({
            a: 1,
            b: 2,
            c: 3,
            d: 4
        }, {
            a: 1,
            d: 1
        }).should.deep.equal({a: 1, d: 4});
    });

    it('should copy complex data', function () {
        home.copyProps([{
            a: 1,
            b: 2,
            c: 3,
            d: [4, 5],
            e: {
                a: 6,
                b: 7,
                c: 8,
                d: 9
            },
            f: [{
                a: 10,
                b: 11,
                c: 12,
                d: 13
            }, {
                b: 14,
                c: 15,
                d: 16
            }]
        }, {
            a: 17,
            c: 19,
            d: [20],
            e: {
                a: 22,
                c: 24,
                d: 25
            },
            f: [{
                c: 28,
                d: 29
            }, {
                b: 30,
                d: 32
            }]
        }], [{
            a: 1,
            b: 1,
            d: [1],
            e: {
                a: 1,
                b: 1,
                c: 1
            },
            f: [{
                a: 1,
                c: 1
            }]
        }]).should.deep.equal([{
            a: 1,
            b: 2,
            d: [4, 5],
            e: {
                a: 6,
                b: 7,
                c: 8
            },
            f: [{
                a: 10,
                c: 12
            }, {
                c: 15
            }]
        }, {
            a: 17,
            d: [20],
            e: {
                a: 22,
                c: 24
            },
            f: [{
                c: 28
            }, {
            }]
        }]);
    });

    it('should work with incorrect types', function () {
        expect(home.copyProps({
            a: 1,
            b: 2,
            c: 3,
            d: 4
        }, 1)).to.be.undefined;

        home.copyProps({
            a: 1,
            b: 2,
            c: 3,
            d: 4
        }, [1]).should.deep.equal([]);

        home.copyProps([1, 2, 3], {a: 1}).should.deep.equal({});

        home.copyProps({
            a: [1, 2, 3]
        }, {
            a: 1
        }).should.deep.equal({});
    });
});
