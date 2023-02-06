const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Webvisor 2 perforcmance check', function () {
    const baseUrl = 'test/webvisor2/';
    const counterId = 42080444;
    it("Doesn't lag too much", async function () {
        const getAverageLagDuration = (file) => {
            const url = baseUrl + file;

            return this.browser
                .timeoutsAsyncScript(6000)
                .url(url)
                .getText('h1')
                .then((innerText) => {
                    const text = innerText;
                    chai.expect(text).to.be.equal('Chunk page');
                })
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options, done) {
                            const lags = [];
                            const observer = new PerformanceObserver(function (
                                list,
                            ) {
                                const entries = list.getEntries();
                                entries.forEach(function (item) {
                                    lags.push(item.duration);
                                });
                            });
                            observer.observe({ entryTypes: ['longtask'] });
                            new Ya.Metrika2({
                                id: options.counterId,
                                webvisor: true,
                            });
                            setTimeout(function () {
                                window.createContentChunk();
                            }, 1000);
                            setTimeout(function () {
                                done(lags);
                            }, 5000);
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(({ value: durations }) => {
                    if (durations.length) {
                        const totalLagDuration = durations.reduce(
                            (prev, val) => prev + val,
                            0,
                        );
                        return totalLagDuration / durations.length;
                    }
                    return 0;
                });
        };

        const oldLag = await getAverageLagDuration(
            'webvisor2-performance-old.hbs',
        );
        const newLag = await getAverageLagDuration('webvisor2-performance.hbs');
        console.log(
            `old webvisor average lag ${oldLag}, new webvisor average lag ${newLag}`,
        );
        chai.expect(newLag).to.be.below(oldLag);
    });
});
