const env = require('../../env');
const grid = require('../services/grid');
const moment = require('moment');
const path = require('path');
const paths = require('../../paths');
const {default: ms} = require('ms');
const {log} = require('../../utils/log');
const {promises: fs} = require('fs');

/**
 * @returns {Promise}
 */
const eraseTmpFolders = () => Promise.all([
    paths.logs,
    paths.retries,
    paths.screenshots,
    paths.chrome.download,
    paths.reporters.allure.report,
    paths.reporters.allure.results,
    paths.reporters.json.report,
].map(async folder => {
    try {
        if (folder.endsWith('logs')) {
            const logs = await fs.readdir(folder);
            await Promise.all(logs.map(file => fs.rm(path.join(folder, file), {force: true})));
        } else {
            await fs.rm(folder, {force: true, recursive: true});
            await fs.mkdir(folder, {recursive: true});
        }
    } catch (err) {
        err.message = `Ошибка при чистке артефактов\n${err.message}`;
        log(err);
    }
}));

/**
 * @returns {string}
 */
const getRunString = () => {
    const {name} = global._testInfo;
    return `npm test --spec=${name}`;
};

/**
 * @returns {string}
 */
const getScreenshotPath = () => {
    const {name} = global._testInfo;
    return `${paths.screenshots}/${name}_${moment().unix()}.png`;
};

/**
 * @param {string} cid
 * @returns {Promise<string>}
 */
const getLogsPaths = async cid => {
    const logs = {
        wdio: `${paths.logs}/wdio-${cid}.log`,
        driver: `${paths.logs}/wdio-chromedriver.log`,
        bro: `${paths.logs}/wdio-${cid}-browser.log`,
    };

    // отдаём путь до лога только если файл существует
    await Promise.all(Object.entries(logs).map(async ([key, value]) => {
        try {
            await fs.stat(path.join(__dirname, '../..', value));
        } catch (err) {
            logs[key] = null;

            if (err.code !== 'ENOENT') {
                err.message += `\n[helpers :: tests] Ошибка при проверке файла логов: ${value}`;
                log(err);
            }
        }
    }));

    return logs;
};

/**
 * @returns {string}
 */
const getRecordUrl = () => `http://${grid.hostname}/video/${browser?.sessionId}`;

/**
 * @param {string} file
 * @returns {string}
 */
const getFileFromTCArtifacts = file => [
    paths.s3.host,
    env.teamcity.project.name,
    env.teamcity.build.name,
    env.teamcity.build.id,
    file.replace(`${paths.artifacts}/`, ''),
].join('/');

/**
 * @param {string} name
 * @returns {Promise<boolean>}
 */
const isTestLastTry = async name => {
    const retryFile = path.join(paths.retries, name);

    let tries;

    try {
        tries = await fs.readFile(retryFile, {encoding: 'utf8'});
    } catch {
        tries = 0;
    }

    const currentTry = Number(tries) + 1;

    await fs.mkdir(path.dirname(retryFile), {recursive: true});
    await fs.writeFile(retryFile, String(currentTry));

    return currentTry - 1 === env.tests.retries;
};

/**
 * @param {Array<{condition: boolean, name: string, fn: Function}>} hooksArr
 * @returns {Promise}
 */
const runHookPromises = hooksArr => Promise.all(hooksArr.map(async elem => {
    const time = Date.now();
    const hookPrefix = `[hook :: ${elem?.name}]`;

    try {
        if (elem.condition) {

            !env.args.isSpec
                && log(`${hookPrefix} start`);

            await elem.fn();

            !env.args.isSpec
                && log(`${hookPrefix} end (${ms(Date.now() - time)})`);
        }
    } catch (err) {
        err.message += `\n${hookPrefix} error (${ms(Date.now() - time)})`;
        log(err);
    }
}));

module.exports = {
    getLogsPaths,
    getRecordUrl,
    getRunString,
    getScreenshotPath,
    getFileFromTCArtifacts,
    isTestLastTry,
    eraseTmpFolders,
    runHookPromises,
};
