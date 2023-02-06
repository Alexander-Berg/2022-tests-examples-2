const path = require('path');

const DEFAULT_OPTIONS = {
    configPath: './tsconfig.json', 
    isolatedModules: true
}

module.exports = (context, options = {}) => {
    const {configPath, isolatedModules} = {...DEFAULT_OPTIONS, ...options};

    return {
        globals: {
            'ts-jest': {
                tsConfig: path.resolve(context, configPath),
                isolatedModules
            }
        },
        roots: [
            '<rootDir>',
            __dirname
        ],
        testTimeout: 10000,
        cacheDirectory: path.resolve(context, './node_modules/.cache/tests'),
        setupFiles: [
            'jest-localstorage-mock',
            path.resolve(__dirname, './src/global.js')
        ],
        moduleNameMapper: {
            // jest-css-modules
            '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$': path.resolve(__dirname, './src/mocks/fileMock.js'),
            '\\.(css|styl)$': path.resolve(__dirname, './src/mocks/styleMock.js')
        },
        moduleFileExtensions: ['js', 'ts', 'tsx', 'json'],
        transform: {
            '^.+\\.(j|t)sx?$': 'ts-jest'
        },
        transformIgnorePatterns: [
            //TODO: amber-blocks надо компилить в ES5 и убрать эту заплатку
            '/node_modules/(?!amber-blocks).+\\.js$'
        ],
        testURL: 'http://localhost',
        testMatch: ['**/__tests__/**/*.(j|t)s?(x)', '**/?(*.)+(spec|test).(j|t)s?(x)'],
        testPathIgnorePatterns: [
            '(.*)/dist'
        ],
        collectCoverage: false
    }
};
