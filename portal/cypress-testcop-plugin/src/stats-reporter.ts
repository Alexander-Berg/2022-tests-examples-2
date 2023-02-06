import Yt from '@yandex-data-ui/yt-javascript-wrapper';
import type {TestSkipsResult} from '@yandex-int/testcop-api';
import {CypressTestcopPluginConfig, CypressTestcopReporterConfig} from './config';
import {createHash} from 'crypto';

const md5Hash = createHash('md5');

export interface IStoredTest {
    time: number;
    testName: string;
    browserId: string;
    project: string;
    tool: string;
    skipped: boolean;
    muted: boolean;
    since: number;
    status: string;
    reason?: string;
    runId: string;
}

export class StatsReporter {
    private _yt: any;
    private _testcopConfig: CypressTestcopPluginConfig;
    private _skipsAndMutes: TestSkipsResult;
    private _reporterConfig: CypressTestcopReporterConfig;
    private _enabled: boolean;

    constructor(
        testcopConfig: CypressTestcopPluginConfig,
        reporterConfig: CypressTestcopReporterConfig,
        skipsAndMutes: TestSkipsResult,
    ) {
        this._enabled = reporterConfig.statsEnabled;
        this._testcopConfig = testcopConfig;
        this._skipsAndMutes = skipsAndMutes;
        this._reporterConfig = reporterConfig;

        if (this._enabled) {
            this._yt = Yt();
            this._yt.setup.setGlobalOption('proxy', reporterConfig.ytProxy);
            this._yt.setup.setGlobalOption('authentication', {
                type: 'oauth',
                token: process.env.YT_OAUTH_TOKEN,
            });
        }
    }

    private async _retry<T>(dReqs: T[], prepare: (a: T, e?: Error) => Promise<T>, times = 5): Promise<Boolean> {
        let reqs = dReqs.map(d => ({
            details: d, promise: prepare(d)
        }));
        let retries = 0;
        while (retries < times && reqs.length > 0) {
            retries += 1;
            console.log('Cypress Testcop Plugin: Fetch attempt #' + retries);
            const testsToShift = reqs.length;
            for (const req of reqs.slice()) {
                try {
                    await req.promise;
                } catch (e) {
                    console.error('Cypress Testcop Plugin: Yt request failed');
                    console.trace(e);
                    reqs.push({
                        details: req.details, promise: prepare(req.details, e)
                    });
                }
            }
            reqs = reqs.slice(testsToShift);
        }

        if (retries === times && reqs.length > 0) {
            return false;
        }
        return retries !== times || reqs.length === 0;
    }

    private _mapTests(
        tests: CypressCommandLine.TestResult[],
        reporterConfig: CypressTestcopReporterConfig,
        testcopConfig: CypressTestcopPluginConfig,
        testcopSkips: TestSkipsResult,
        time: number,
        runId: string,
    ): IStoredTest[] {
        return tests.map((test, i) => {
            const testName = `${test.title.join(' ')}.${reporterConfig.browser}`;
            let status = test.state;

            if (status === 'failed') {
                status = 'fail';
            } else if (status === 'passed') {
                status = 'success';
            } else if (status === 'pending') {
                status = 'skipped';
            }

            return {
                time: time + i,
                testName,
                browserId: reporterConfig.browser,
                project: testcopConfig.project,
                tool: testcopConfig.tool,
                skipped: Boolean(testcopSkips.skips[testName]),
                muted: Boolean(testcopSkips.mutes[testName]),
                since: testcopSkips.skips[testName] ? Number(new Date(testcopSkips.skips[testName].timestamp)) : 0,
                status,
                reason: testcopSkips.skips[testName]?.reason || testcopSkips.mutes[testName]?.reason,
                runId,
            };
        });
    }

    _createRunHash(
        report: CypressCommandLine.CypressRunResult,
        testcopConfig: CypressTestcopPluginConfig,
        reporterConfig: CypressTestcopReporterConfig,
    ) {
        return md5Hash.update(
            report.cypressVersion + '-' + reporterConfig.browser + '-' +
            testcopConfig.project + '-' + testcopConfig.tool
        ).digest('hex');
    }

    async report(
        report: CypressCommandLine.CypressRunResult
    ) {
        if (!this._enabled) {
            console.log('Cypress Testcop Plugin: Skipping stats');
            return;
        }
        console.log('Cypress Testcop Plugin: Saving stats...');
        const allTests = report.runs.reduce((a, v) => a.concat(v.tests), []);
        const runId = `${Date.now()}-${this._createRunHash(report, this._testcopConfig, this._reporterConfig)}`;
        const time = Date.now();
        const testsToStore = this._mapTests(
            allTests, this._reporterConfig, this._testcopConfig, this._skipsAndMutes, time, runId
        );
        const isSuccess = await this._retry([testsToStore], tests => {
            return this._yt.v3.insertRows({
                parameters: {
                    path: this._reporterConfig.ytPath,
                    'input_format': {
                        $value: 'json',
                        $attributes: {
                            'string_length_limit': 1024,
                            'encode_utf8': 'false',
                            stringify: 'true',
                            'annotate_with_types': 'true'
                        }
                    }
                },
                data: tests
            });
        });

        if (isSuccess) {
            console.log('Cypress Testcop Plugin: Stats saved');
        } else {
            console.error('Cypress Testcop Plugin: Error saving full stats');
        }
    }
}
