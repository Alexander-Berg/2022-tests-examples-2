const path = require('path');
const Mocha = require('mocha');
const glob = require('glob');
const rimraf = require("rimraf");
const fs = require('fs');
const fsPromises = fs.promises;
const Server = require('karma').Server;
const cfg = require('karma').config;
const {generatePageConfigs} = require('../../generate-config');
const webpack = require('webpack');

/**
 * @returns {Promise<string[]>} пути до сгенерированных бандлов
 */
const generateTestBundles = async ({
     alias,
     bundles,
     mapBundleNameToTestBundleName,
     buildFolderPath,
     entryPath,
     clientSide,
     serverSide
 }) => {
    const entryTemplateContent = fs.readFileSync(entryPath, "utf8");
    if (!fs.existsSync(buildFolderPath)){
        fs.mkdirSync(buildFolderPath);
    }
    const webpackConfigs = await Promise.all(
        Object.entries(bundles)
            .map(async ([bundleName, {levelsPaths, folderPath}]) => {
                const entryContent = entryTemplateContent.replace(
                    /__INJECTED_LEVEL_PATH__/g,
                    `'${folderPath}'`
                );
                const entryPath = path.resolve(buildFolderPath, `${bundleName}.js`);
                await fsPromises.writeFile(entryPath, entryContent);
                const output = mapBundleNameToTestBundleName(bundleName);
                return generatePageConfigs({
                    entry: {[output]: entryPath},
                    resolveModules: levelsPaths,
                    devtool: 'inline-source-map',
                    alias,
                    clientSide,
                    serverSide,
                    shouldRemoveServerSideStuff: false,
                    shouldUseAssetsPlugin: false,
                    output: {
                        serverPath: buildFolderPath,
                        clientPath: buildFolderPath,
                        filename: output,
                    }
                })[0];
            })
    );

    await new Promise(((resolve, reject) => {
        webpack(webpackConfigs, (err, stats) => {
            if (err || stats.hasErrors()) {
                console.error(stats.toJson('minimal'));
                reject();
            }
            resolve();
        });
    }));

    return Object.entries(bundles)
        .map(([bundleName]) => path.resolve(buildFolderPath, mapBundleNameToTestBundleName(bundleName)));
};

const dispose = (directoryPath) => {
    return new Promise(((resolve, reject) => {
        rimraf(directoryPath, (e) => {
            if (e) {
                reject(e);
            }
            resolve();
        });
    }));
};

const copySnaps = (sourceDirectory, destinationDirectory) => {
    return new Promise(((resolve, reject) => {
        glob('*.snap', {
            cwd: sourceDirectory
        }, (err, files) => {
            const promises = files.map(source => {
                const destinationPath = path.resolve(destinationDirectory, path.basename(source));
                const sourcePath = path.resolve(sourceDirectory, source);
                return fsPromises.copyFile(sourcePath, destinationPath);
            });
            Promise.all(promises).then(resolve, reject);
        });
    }));
};

/**
 * @typedef {Object} bundle
 * @property {array} levelsPaths - как резолвить импорты для данного бандла
 * @property {string} folderPath - директория откуда импортировать тесты
 *
 * Функция для прохождения тестов шаблонов
 * @param mochaOptions - https://github.com/mochajs/mocha/wiki/Using-Mocha-programmatically
 * @param alias
 * @param testingAssertsDirectory - директория хранения снапов
 * @param {Object.<string, bundle>} bundles
 * @returns {Promise}
 */
 const runTemplateTests = async ({
        mochaOptions,
        alias,
        bundles,
        testingAssertsDirectory,
    }) => {
    const BUILD_FOLDER_PATH = path.resolve(__dirname, 'template-testing-asserts');
    try {
         const paths = await generateTestBundles({
             alias,
             bundles,
             mapBundleNameToTestBundleName: (bundleName) => `${bundleName}-view.tests.js`,
             buildFolderPath: BUILD_FOLDER_PATH,
             entryPath: path.resolve(__dirname, './template-testing-entry.js'),
             serverSide: true
         });

         await new Promise((resolve) => {
             const mocha = new Mocha(mochaOptions);
             paths.forEach((p) => mocha.addFile(p));
             mocha.run(function(failures) {
                 process.exitCode = failures ? 1 : 0;  // exit with non-zero status if there were failures
                 resolve();
             });
         });
     } finally {
         await copySnaps(BUILD_FOLDER_PATH, testingAssertsDirectory);
         await dispose(BUILD_FOLDER_PATH);
     }
};

/**
 * @typedef {Object} bundle
 * @property {array} levelsPaths - как резолвить импорты для данного бандла
 * @property {string} folderPath - директория откуда импортировать тесты
 *
 * Функция для прохождения тестов шаблонов
 * @param alias
 * @param karmaConfigPath - путь до конфига кармы
 * @param {Object.<string, bundle>} bundles
 * @returns {Promise}
 */
const runSpecTests = async ({
    alias,
    bundles,
    karmaConfigPath,
}) => {
    const BUILD_FOLDER_PATH = path.resolve(__dirname, 'spec-testing-asserts');
    try {
        const paths = await generateTestBundles({
            alias,
            bundles,
            mapBundleNameToTestBundleName: (bundleName) => `${bundleName}-spec.tests.js`,
            buildFolderPath: BUILD_FOLDER_PATH,
            entryPath: path.resolve(__dirname, './spec-testing-entry.js'),
            clientSide: true
        });

        const karmaConfig = cfg.parseConfig(karmaConfigPath, {
            files: paths.map((p) => ({ pattern: p, watched: false })),
        });

        await new Promise(((resolve) => {
            const server = new Server(karmaConfig, function(exitCode) {
                process.exitCode = exitCode ? 1 : 0;
                resolve();
            });
            server.start();
        }));
    } finally {
        await dispose(BUILD_FOLDER_PATH);
    }
};

module.exports = {
    runTemplateTests,
    runSpecTests
};

