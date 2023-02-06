import * as path from 'path';
import * as vm from 'vm';
import fs from 'fs';
import webpack from 'webpack';
// eslint-disable-next-line import/no-extraneous-dependencies
import TerserPlugin from 'terser-webpack-plugin';
import ReDefinePlugin from 'webpack-stub/build-src/ReDefinePlugin';
import pathsPlugin from '../../babel/pathsBabelPlugin';
import transformViewsUsageRef from '../../babel/transformViewsUsageRef';
import transformCachedDecl from '../../babel/transformCachedDecl';

const attributesGetterPath = require.resolve('webpack-stub/utils/attributes-getter');
const childMapperPath = require.resolve('webpack-stub/utils/child-mapper');

export async function buildClientBundle(rootDir: string, entry: string, lastLevel: string) {
    let clientConfig: webpack.Configuration = {
        mode: 'production',
        entry: {
            client: entry
        },
        target: 'web',
        node: {
            global: true
        },
        output: {
            path: rootDir + '/dist',
            library: {
                type: 'this'
            }
        },
        optimization: {
            concatenateModules: true,
            minimize: true,
            minimizer: [new TerserPlugin({
                terserOptions: {
                    compress: {
                        // to keep returned exports
                        negate_iife: false,
                        side_effects: false
                    }
                }
            })],
        },
        resolve: {
            extensions: ['.ts', '.tsx', '.js', '.jsx']
        },
        plugins: [
            new ReDefinePlugin({
                'req.isClient': true,
                IS_CLIENT: true,
                IS_DEV: false
            })
        ],
        module: {
            rules: [
                {
                    test: /\.[jt]sx?$/,
                    exclude: /node_modules/,
                    use: {
                        loader: require.resolve('babel-loader'),
                        options: {
                            // Не кешируем тесты из-за возможной смены файлов
                            cacheDirectory: false,
                            presets: [
                                [require.resolve('@babel/preset-env'), {
                                    // useBuiltIns: 'usage',
                                    useBuiltIns: false,
                                    // corejs: 3,
                                    targets: [
                                        'Safari > 7',
                                        'Firefox > 27',
                                        'Chrome >= 21',
                                        'ie >= 10',
                                        'edge >= 12',
                                        'last 2 versions',
                                        '>1%'
                                    ],
                                    modules: false,
                                    exclude: [
                                        'transform-typeof-symbol'
                                    ]
                                }]
                            ],
                            plugins: [
                                ['@babel/plugin-transform-typescript', {
                                    isTSX: true,
                                    onlyRemoveTypeImports: true
                                }],
                                [pathsPlugin, {
                                    lastLevel,
                                    levelsPath: path.resolve(rootDir, 'levels.json')
                                }],
                                [transformViewsUsageRef, {
                                    levelsPath: path.resolve(rootDir, 'levels.json')
                                }],
                                [transformCachedDecl],
                                [require('webpack-stub/utils/this-replacing-babel-plugin'), {}],
                                // '@babel/plugin-syntax-dynamic-import',
                                [require('webpack-stub/utils/jsx-babel-plugin'), {
                                    pragma: 'execView',
                                    throwIfNamespace: false,
                                    useBuiltIns: true,
                                    pragmaFrag: 'makeFrag',
                                    attributesGetterPath,
                                    childMapperPath
                                }]
                            ]
                        }
                    }
                }
            ]
        }
    };
    const compiler = webpack(clientConfig);

    return new Promise<void>((resolve, reject) => {
        compiler.run((err: Error | undefined, stats) => {
            try {
                if (err) {
                    reject(err);
                    return;
                } else if (stats && stats.hasErrors()) {
                    const json = stats.toJson();
                    if (json.errors) {
                        reject(new Error(json.errors.length > 1 ? json.errors.join() : String(json.errors[0])));
                    } else {
                        reject(new Error('Unknown'));
                    }
                    return;
                }

                resolve();
            } catch (err2) {
                reject(err2);
            }
        });
    });
}

export function getClientBundleContents(rootDir: string) {
    return fs.readFileSync(path.resolve(rootDir, 'dist', 'client.js'), 'utf-8');
}

export function getClientFunc(rootDir: string, functionName: string) {
    const fileContent = getClientBundleContents(rootDir);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let contextBase: { [key: string]: any } = {};
    let context = vm.createContext(contextBase);
    vm.runInContext(fileContent, context);

    return context[functionName];
}
