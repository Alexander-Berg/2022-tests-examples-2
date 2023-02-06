import {AssertionError} from 'chai';
import colors from 'colors';
import {diffLines} from 'diff';
import fs from 'fs-extra';
import path from 'path';

import {assertDefined} from '@/src/utils/assert-defined';

type AnyObject = Partial<Record<string, unknown>>;
type AssertionErrorInfo = typeof AssertionError & {expected: unknown; actual: unknown};

/**
 * @description Директория для храниения snapshot'ов (создается автоматически в директории с тестом)
 */
const SNAPSHOT_DIR = '__snapshots__';

/**
 * @description Количество отступов для форматирования JSON
 */
const INDENT_COUNT = 2;

/**
 * @description Кеш импортированных модулей - snapshot'ов
 */
const cache = new Map<string, AnyObject>();

/**
 * @description Счетчик snapshot'ов в пределах одного теста
 */
const counters = new Map<string, number>();

/**
 * @description Получение `expected` значения из модуля - snapshot'а
 */
function getSnapshotEntry(pathToFile: string, entryName: string) {
    let snapshotObject = {} as AnyObject;
    if (cache.has(pathToFile)) {
        snapshotObject = assertDefined(cache.get(pathToFile));
    } else if (fs.existsSync(pathToFile)) {
        snapshotObject = require(pathToFile);
        cache.set(pathToFile, snapshotObject);
    }
    if (entryName in snapshotObject) {
        return snapshotObject[entryName];
    }
    throw new Error('Snapshot does not exists');
}

/**
 * @description Обновление модуля - snapshot'а
 */
function saveSnapshotEntry(pathToFile: string, entryName: string, data: unknown) {
    fs.ensureDirSync(path.dirname(pathToFile));
    cache.set(pathToFile, {...cache.get(pathToFile), [entryName]: data});
    const cached = assertDefined(cache.get(pathToFile));
    const content = Object.entries(cached)
        .map(([key, value]) => `exports[\`${key}\`] = ${JSON.stringify(value, null, INDENT_COUNT)};`)
        .join('\n');

    fs.writeFileSync(pathToFile, content);
}

/**
 * @description Получение имени поля (ключа) в модуле - snapshot'е для конкретного теста
 */
function getEntryName(test: Hermione.Test) {
    const counter = (counters.get(test.uuid) || 0) + 1;
    counters.set(test.uuid, counter);
    return `${test.fullTitle()} ${counter}`;
}

/**
 * @description Форматирование диффа сравнения snapshot'ов в наглядный вид
 */
function getPrintableDiff(diff: Diff.Change[]) {
    return diff
        .filter(({added, removed}) => added || removed)
        .map(({added, value}) => {
            const sign = added ? '+' : '-';
            const color = added ? colors.green : colors.red;
            const formatted = `${sign} ${value.trim().split('\n').join(`\n ${sign}`)}`;
            return color(formatted);
        })
        .join('\n');
}

/**
 * @description Функция - плагин для записи нового метода в прототип `Chai`
 */
function matchSnapshot(chai: Chai.ChaiStatic, utils: Chai.ChaiUtils) {
    utils.addMethod(chai.Assertion.prototype, 'matchSnapshot', function (this: Chai.Assertion, ctx: Hermione.Context) {
        const actual = utils.flag(this, 'object');
        const shouldUpdate = Boolean(process.env.CHAI_SNAPSHOT_UPDATE);

        const test = ctx.currentTest;
        const dirName = path.dirname(test.file).replace('/out', '');
        const fileName = path.basename(test.file).replace(/\.(js|ts)x?$/, '.snap');

        const snapshotFile = path.join(dirName, SNAPSHOT_DIR, fileName);
        const entryName = getEntryName(test);

        try {
            const expected = getSnapshotEntry(snapshotFile, entryName);
            chai.assert.deepEqual(actual, expected);
        } catch (error) {
            if (shouldUpdate) {
                return saveSnapshotEntry(snapshotFile, entryName, actual);
            }
            if (isAssertionErrorInfo(error)) {
                const expected = JSON.stringify(error.expected, null, INDENT_COUNT);
                const actual = JSON.stringify(error.actual, null, INDENT_COUNT);
                const diffResult = diffLines(actual, expected, {newlineIsToken: true});
                throw new Error(["Snapshot didn't match\n", getPrintableDiff(diffResult), ''].join('\n'));
            }
            throw error;
        }
    });
}

/**
 * @description Type guard - является ли ошибка ошибкой сравнения snapshot'ов
 */
function isAssertionErrorInfo(error: unknown): error is AssertionErrorInfo {
    return error instanceof AssertionError && 'expected' in error && 'actual' in error;
}

export {matchSnapshot};
