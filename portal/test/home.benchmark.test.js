describe('home.benchmark', function() {
    it('works as expected', function() {
        var i = 0,
            emptyFunc = function () {
            };
        var benchmark = home.benchmark(
            // Emulate of runner
            {
                start: function () {
                },
                get: function () {
                    return i;
                }
            }
        );

        for (; i < 10; i++) {
            benchmark.log(emptyFunc, 'xxx', 'tests');
        }

        for (; i < 20; i++) {
            benchmark.log(emptyFunc, 'xxx3', 'tests');
        }

        benchmark.dump().should.deep.equal({
            summary: 190,
            tests: {
                xxx: {
                    runs: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                    calls: 10,
                    selfTime: 45,
                    totalTime: 45,
                    selfAvg: 4.5,
                    min: 0,
                    max: 9,
                    percent: '23.684',
                    optimizationStatus: undefined
                },
                xxx3: {
                    runs: [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
                    calls: 10,
                    selfTime: 145,
                    totalTime: 145,
                    selfAvg: 14.5,
                    min: 10,
                    max: 19,
                    percent: '76.316',
                    optimizationStatus: undefined
                }
            }
        });
    });
});
