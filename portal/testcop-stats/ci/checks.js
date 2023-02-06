const makeGraph = require('./makeGraph');

makeGraph({
    Eslint: 'npm run eslint',
    Jest: ['npm run jest', {
        report: '__reports/report-unit',
        reportParams: {
            attributes: {
                type: 'jest-report',
            },
        },
        main: 'index.html',
        type: 'html',
    }],
}, {
    Eslint: null,
    Jest: null
});
