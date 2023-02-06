/* eslint no-console:0 */
const {Graph} = require('@yandex-int/tkit');
const {steps} = require('./steps');

const createTreeConfiguration = () => {
    // Конфигурация сборки.
    // Описывает порядок выполнения шагов.
    return {
        EslintChecks: null,
        EslintFullChecks: null,
        Typecheck: null,
        Jest: null,
    };
};

(async function () {

    const graph = new Graph({
        repo: {},
        subscribers: [],
        failOnStepFailure: false,
        selective: true,
        hideIntermediate: true,
        stopOnUpdate: false,
        sendSummaryAsync: async () => {}
    });

    const treeConfig = createTreeConfiguration();

    return graph.run(treeConfig, steps);
})()
    .catch((err) => {
        console.trace(err);
        process.exit(1);
    });
