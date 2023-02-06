const config = require('./.hermione.conf.js');

module.exports = {
    ...config,
    sets: {
        desktop: {
            files: [
                'tests/ft/e2e/counters/counter-create-test.js',
                'tests/ft/e2e/counters/counter-list-test.js',
                'tests/ft/e2e/counters/goals/goal-create-test.js',
                'tests/ft/e2e/counters/goals/goal-change-order-test.js',
                'tests/ft/e2e/counters/grants/grant-create-test.js',
                'tests/ft/e2e/counters/grants/grant-create-negative-test.js',
                'tests/ft/e2e/reports/dashboards/dashboard-create-widget-test.js',
                'tests/ft/e2e/reports/dashboards/dashboard-clean-and-restore-test.js',
                'tests/ft/e2e/promo-page-test.js',
                'tests/ft/e2e/only-ps/bug-for-external-users-test.js',
                'tests/ft/e2e/calls/create-track-test.js'
            ],
            browsers: ['chrome']
        }
    },
    baseUrl: 'https://metrika-ng-ps.yandex.ru',
    system: {
        ctx: {
            baseUrl: 'https://metrika-ng-ps.yandex.ru'
        },
        workers: 30,
        testsPerWorker: 1
    }
};
