import * as path from 'path';
import * as fs from 'fs';

import { PluginItem, transform } from '@babel/core';

import replaceTestDepsPlugin from './babel/replaceTestDepsPlugin';
import pathsPlugin from './babel/pathsBabelPlugin';
import appendViewNamePlugin from './babel/appendViewName';
import transformViewsUsageStringPlugin from './babel/transformViewsUsageString';

import { getLevels } from './pathsUtils';

const childMapperPath = require.resolve('webpack-stub/utils/child-mapper');
const attributesGetterPath = require.resolve('webpack-stub/utils/attributes-getter');

const globalLevels = path.resolve(__dirname, '../levels.json');

function findLevelsPath(filename: string): string {
    let currentDir = path.dirname(filename);
    while (currentDir !== '/') {
        const localLevels = path.resolve(currentDir, 'levels.json');
        if (fs.existsSync(localLevels)) {
            return localLevels;
        }
        currentDir = path.dirname(currentDir);
    }
    return globalLevels;
}

export function process(src: string, filename: string) {
    const plugins: PluginItem[] = [
        ['@babel/plugin-transform-typescript', {
            isTSX: true,
            onlyRemoveTypeImports: true
        }],
        [require('webpack-stub/utils/jsx-babel-plugin'), {
            pragma: 'execView',
            throwIfNamespace: false,
            useBuiltIns: true,
            pragmaFrag: 'makeFrag',
            attributesGetterPath,
            childMapperPath,
            modifyFunctionParamsExclude: /\.view\.test\.tsx/
        }]
    ];

    const levelsPath = findLevelsPath(filename);
    const levels = getLevels(filename, levelsPath);

    if (
        filename.endsWith('.view.tsx') || filename.endsWith('.view.js') ||
        filename.endsWith('.view.jsx') ||
        filename.endsWith('.test.tsx') || filename.endsWith('.test-data.tsx')
    ) {
        plugins.push(
            [appendViewNamePlugin, {}],
            [transformViewsUsageStringPlugin, {}]
        );
    }

    if (filename.endsWith('.test.tsx') || filename.endsWith('.test.ts') || filename.endsWith('.test-data.tsx')) {
        plugins.push(
            [replaceTestDepsPlugin, {
                levelsPath
            }]
        );
    }

    plugins.push(
        [pathsPlugin, {
            lastLevel: levels.length ? levels[0].resolvedPath : undefined,
            levelsPath
        }]
    );

    const result = transform(src, {
        filename,
        presets: [
            'jest',
            [
                '@babel/preset-env',
                {
                    targets: {
                        node: 'current'
                    }
                }
            ]
        ],
        sourceMaps: 'inline',
        plugins
    });

    return result ? result.code : src;
}
