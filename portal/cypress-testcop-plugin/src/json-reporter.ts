import {promises as fsPromises} from 'fs';
import type {TestSkipsResult} from '@yandex-int/testcop-api';
import {CypressTestcopPluginConfig, CypressTestcopReporterConfig} from './config';
import {testsToJson} from './testcop-convert';

const {readFile, writeFile} = fsPromises;

export class JsonReporter {
    private _skipsAndMutes: TestSkipsResult;
    private _reportFile: string;
    private _browser: string;
    private _enabled: boolean;

    constructor(
        _: CypressTestcopPluginConfig,
        reporterConfig: CypressTestcopReporterConfig,
        skipsAndMutes: TestSkipsResult,
    ) {
        this._skipsAndMutes = skipsAndMutes;
        this._reportFile = reporterConfig.reportFile;
        this._browser = reporterConfig.browser;
        this._enabled = reporterConfig.jsonEnabled !== false;
    }

    public async report(report: CypressCommandLine.CypressRunResult) {
        if (!this._enabled) {
            return;
        }

        let jsonReport = testsToJson(report, this._skipsAndMutes, {browser: this._browser});
        try {
            const data = await readFile(this._reportFile);
            if (data) {
                try {
                    jsonReport = {...JSON.parse(data.toString()), ...jsonReport};
                } catch (e) {
                    console.error('Cypress Testcop Plugin: unknown data in cypress-report.json file');
                    console.trace(e);
                }
            }
        } catch (e) {
            console.log('Cypress Testcop Plugin: empty cypress-report.json file. Skipping');
        }

        try {
            await writeFile(this._reportFile, JSON.stringify(jsonReport));
            console.log('Cypress Testcop Plugin: Report saved to ' + this._reportFile);
        } catch (er) {
            console.error('Cypress Testcop Plugin: Cypress run failed. Report not saved');
            console.trace(er);
        }
    }
}
