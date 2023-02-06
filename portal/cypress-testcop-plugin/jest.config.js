module.exports = {
    preset: 'ts-jest',
    testEnvironment: 'node',
    reporters: [
        'default',
        [
            'jest-html-reporter',
            {
                outputPath: '<rootDir>/.reports/units/index.html',
                pageTitle: 'Cupress Testcop Plugin report',
                includeFailureMsg: true,
                includeConsoleLog: true,
                includeSuiteFailure: true,
                includeObsoleteSnapshots: true,
            },
        ],
    ],
    globals: {
        'ts-jest': {
            tsconfig: 'test/tsconfig.json',
        },
    },
};
