const path = require('path');

const steps = {
    /* Здесь проверяются только изменённые скрипты */
    EslintChecks: [
        'node --max-old-space-size=8192 ./node_modules/.bin/eslint --quiet --ext .js,.ts %s',
        {
            files: [
                '**.js',
                '**.ts'
            ],
            partialRun: true
        }
    ],
    /* Здесь проверяются все скрипты при изменении конфигов */
    EslintFullChecks: [
        'node --max-old-space-size=8192 ./node_modules/.bin/eslint --quiet --ext .js,.ts, src test ci',
        {
            files: [
                '.eslintrc.json'
            ]
        }
    ],
    Jest: [
        'npm run test',
        {
            report: path.join('.reports', 'units'),
            main: 'index.html',
            type: 'html',
            files: [
                'src/**',
                'test/**',
                'package.json',
                'package-lock.json',
                '.eslintrc.js',
                'tsconfig.json',
                '!*.md'
            ]
        }
    ],
    Typecheck: [
        'npm run typecheck',
        {
            files: [
                '**/*.ts',
                'package.json',
                'package-lock.json',
                'tsconfig.json'
            ]
        }
    ],
};

module.exports = {
    steps
};
