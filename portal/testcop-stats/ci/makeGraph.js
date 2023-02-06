/* eslint-env es6 */
/* eslint no-console: 0 */
const {Graph} = require('@yandex-int/tkit');

module.exports = (steps, graphConfig) => {
    let subscribers = [];

    const graph = new Graph({
        lifetime: 30 * 60 * 1000,
        repo: {},
        subscribers,
        hideIntermediate: true,
    });

    return graph
        .run(graphConfig, steps)
        .catch(err => {
            console.error(err);
            process.exit(1);
        });
};
