import type {TestSkipsResult} from '@yandex-int/testcop-api';
import {IJsonTests, testsToJson, ITestsToJsonParams} from '../src/testcop-convert';
import failedTestSuite from './fixtures/failed-test.json';
import skippedTestSuite from './fixtures/skipped-test.json';
import skippedTestSuite2 from './fixtures/skipped-test2.json';
import mutedTestSuite from './fixtures/muted-test.json';
import passedTestSuite from './fixtures/passed-test.json';

for (const [name, testCase] of [
    ['Failed test', failedTestSuite],
    ['Skipped test', skippedTestSuite],
    ['Skipped test, no reason', skippedTestSuite2],
    ['Muted test', mutedTestSuite],
    ['Passed test', passedTestSuite],
] as [string, typeof skippedTestSuite][]) {
    test(name, () => {
        const results = testCase[0] as unknown as CypressCommandLine.CypressRunResult;
        const testcop = testCase[1] as unknown as TestSkipsResult;
        const params = testCase[2] as unknown as ITestsToJsonParams;
        const ans = testCase[3] as unknown as IJsonTests;
        expect(testsToJson(results, testcop, params)).toEqual(ans);
    });
}
