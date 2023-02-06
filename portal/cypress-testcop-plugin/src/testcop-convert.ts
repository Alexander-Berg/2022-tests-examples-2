import type {TestSkipsResult} from '@yandex-int/testcop-api';

export interface IJsonTests {
    [key: string]: {
        suitePath: string[];
        fullName: string;
        browserId: string;
        file: string;
        duration?: null | number;
        meta?: {
            muted?: boolean;
            browserVersion?: string;
            muteReason?: string;
        },
        status: 'skipped' | 'failed' | 'success' | string;
        skipReason?: string;
        errorReason?: {
            message: string;
            stack: string;
        };
        retries?: {
            message: string;
            stack: string;
        }[];
    }
}

const makeSkippedTest = (
    results: CypressCommandLine.CypressRunResult,
    run: CypressCommandLine.RunResult,
    test: CypressCommandLine.TestResult,
    testcop: TestSkipsResult): IJsonTests => {
    const testName = test.title.join(' ');
    const testHash = `${testName}.${results.browserName}`;
    const skipReason = testcop.skips[testHash] ?
        testcop.skips[testHash].reason : 'Skipped for some reason';

    const isMuted = Boolean(testcop.mutes[testHash]);
    const muteReason = testcop.mutes[testHash] ?
        testcop.mutes[testHash].reason : 'Muted for some reason';
    return {
        [testHash]: {
            suitePath: test.title,
            fullName: testName,
            browserId: results.browserName,
            file: run.spec.relative,
            duration: null,
            meta: {
                muted: isMuted,
                browserVersion: results.browserVersion,
                muteReason: isMuted ? muteReason : undefined,
            },
            status: 'skipped',
            skipReason: isMuted ? muteReason : skipReason,
        },
    };
};

const makeDefaultTest = (
    results: CypressCommandLine.CypressRunResult,
    run: CypressCommandLine.RunResult,
    test: CypressCommandLine.TestResult): IJsonTests => {
    const testName = test.title.join(' ');
    const testHash = `${testName}.${results.browserName}`;
    return {
        [testHash]: {
            suitePath: test.title,
            fullName: testName,
            browserId: results.browserName,
            file: run.spec.relative,
            duration: null,
            meta: {
                muted: false,
                browserVersion: results.browserVersion,
            },
            status: test.state,
        },
    };
};

const makePassedTest = (
    results: CypressCommandLine.CypressRunResult,
    run: CypressCommandLine.RunResult,
    test: CypressCommandLine.TestResult
): IJsonTests => {
    const testName = test.title.join(' ');
    const testHash = `${testName}.${results.browserName}`;

    return {
        [testHash]: {
            suitePath: test.title,
            fullName: testName,
            browserId: results.browserName,
            file: run.spec.relative,
            duration: test.attempts.reduce((a, at) => at.duration + a, 0),
            meta: {
                muted: false,
                browserVersion: results.browserVersion,
            },
            status: 'success'
        },
    };
};

const makeFailedTest = (
    results: CypressCommandLine.CypressRunResult,
    run: CypressCommandLine.RunResult,
    test: CypressCommandLine.TestResult
): IJsonTests => {
    const testName = test.title.join(' ');
    const testHash = `${testName}.${results.browserName}`;

    const retries = test.attempts.map(a => ({
        message: a.error?.message,
        stack: a.error?.stack
    }));

    return {
        [testHash]: {
            suitePath: test.title,
            fullName: testName,
            browserId: results.browserName,
            file: run.spec.relative,
            duration: test.attempts.reduce((a, at) => at.duration + a, 0),
            meta: {
                muted: false,
                browserVersion: results.browserVersion,
            },
            status: 'fail',
            errorReason: retries[retries.length - 1],
            retries,
        }
    };
};

const convertTest = (
    results: CypressCommandLine.CypressRunResult,
    run: CypressCommandLine.RunResult,
    test: CypressCommandLine.TestResult,
    testcop: TestSkipsResult,
    params: ITestsToJsonParams,
): IJsonTests => {
    // No need in deep copy
    const modifiedResults = {...results};
    if (params.browser) {
        modifiedResults.browserName = params.browser;
    }

    if (test.state === 'failed') {
        return makeFailedTest(modifiedResults, run, test);
    }
    if (test.state === 'passed') {
        return makePassedTest(modifiedResults, run, test);
    }
    if (test.state === 'pending' || test.state === 'skipped') {
        return makeSkippedTest(modifiedResults, run, test, testcop);
    }
    return makeDefaultTest(modifiedResults, run, test);
};

export interface ITestsToJsonParams {
    browser?: string;
}
/**
 * Converts cypress tests to Hermione like json report
 * @param results
 * @param testcop
 * @param params
 * @returns
 */
export const testsToJson = function (
    results: CypressCommandLine.CypressRunResult,
    testcop: TestSkipsResult,
    params: ITestsToJsonParams): IJsonTests {
    const result: IJsonTests = {};
    const runs = results.runs;
    for (const run of runs) {
        if (!run.tests) {
            console.log('Cypress Testcop Plugin: All tests failed inside run. Skipping');
            continue;
        }
        for (const test of run.tests) {
            const newTest = convertTest(results, run, test, testcop, params);
            const [key, value] = Object.entries(newTest)[0];
            result[key] = value;
        }
    }
    return result;
};
