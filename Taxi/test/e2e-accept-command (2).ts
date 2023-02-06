import execa from 'execa';
import fs from 'fs';
import got from 'got/dist/source';
import path from 'path';
import tar from 'tar';

import {PATH_TO_HERMIONE_CONFIG, PATH_TO_HERMIONE_HTML_REPORT} from 'cli/test/constants';
import {writeInfo} from 'cli/test/utils';
import {CliUsage, defaultHelpArg} from 'cli/util';
import {config} from 'service/cfg';
import {assertNumber} from 'service/helper/assert-number';
import {assertString} from 'service/helper/assert-string';

const ARC_API_URL = 'https://arcanum.yandex.net/api/v1';
const TEAM_CITY_API_URL = 'https://teamcity.taxi.yandex-team.ru';
const TESTS_TYPE = 'YandexTaxiProjects_Lavka_Birds_PullRequests_PullRequests';
const TESTS_SYSTEM = 'teamcity-taxi';

type Check = {
    system: string;
    type: string;
    status: string;
    system_check_uri?: string;
};

export interface HandleInput {
    help?: boolean;
}

export const usage: CliUsage<HandleInput> = {
    parse: {
        help: defaultHelpArg
    },
    options: {helpArg: 'help'}
};

export async function handle() {
    const prId = await getPrId();
    const reportUrl = await getReportUrl(prId);

    const unpackTo = path.dirname(PATH_TO_HERMIONE_HTML_REPORT);

    if (fs.existsSync(PATH_TO_HERMIONE_HTML_REPORT)) {
        fs.rmdirSync(PATH_TO_HERMIONE_HTML_REPORT, {recursive: true});
    } else {
        fs.mkdirSync(unpackTo, {recursive: true});
    }

    await download(reportUrl, unpackTo);
    writeInfo(`Report for PR id = "${prId}" was downloaded and unpacked into ${PATH_TO_HERMIONE_HTML_REPORT}`);

    return await execa('npx', [config.cli.hermioneBinary, 'gui', '--config', PATH_TO_HERMIONE_CONFIG], {
        stdout: 'inherit',
        stderr: 'inherit'
    });
}

async function getPrId() {
    try {
        const {stdout} = await execa('arc', ['pr', 'st']);
        const [header] = stdout.split('\n');
        const [_, id] = header.split(/\s+/);
        return assertNumber(id, {coerce: true});
    } catch (error) {
        throw new Error(`Failed to determine PR id: ${error.message}`);
    }
}

async function getReportUrl(prId: number) {
    const arcApiToken = await getArcApiToken();

    const response = await got<{data: {checks: Check[]}}>(
        `${ARC_API_URL}/review-requests/${prId}?fields=checks(system,type,status,system_check_uri)`,
        {
            headers: {
                Authorization: `OAuth ${arcApiToken}`
            },
            responseType: 'json',
            resolveBodyOnly: true,
            https: {
                rejectUnauthorized: false
            }
        }
    );

    const testsCheck = response.data.checks.find(({type, system}) => type === TESTS_TYPE && system === TESTS_SYSTEM);

    if (!testsCheck) {
        throw new Error('No test check found for current PR');
    }

    if (testsCheck.status === 'pending') {
        throw new Error('Pending test check status found. Wait and try again later.');
    }

    const systemCheckUri = assertString(testsCheck.system_check_uri);
    const {searchParams} = new URL(systemCheckUri);

    const buildId = assertString(searchParams.get('buildId'));
    const buildTypeId = assertString(searchParams.get('buildTypeId'));
    return `${TEAM_CITY_API_URL}/repository/download/${buildTypeId}/${buildId}:id/reports.tar.gz`;
}

async function getTeamCityApiToken() {
    const {stdout} = await execa('bash', ['-c', 'echo $TEAM_CITY_TAXI_API_TOKEN']);
    return assertString(stdout, {errorMessage: 'Environment variable "TEAM_CITY_TAXI_API_TOKEN" is not set'});
}

async function getArcApiToken() {
    const {stdout} = await execa('bash', ['-c', 'echo $ARC_API_TOKEN']);
    return assertString(stdout, {errorMessage: 'Environment variable "ARC_API_TOKEN" is not set'});
}

async function download(resourceUrl: string, unpackTo: string): Promise<void> {
    const teamCityApiToken = await getTeamCityApiToken();
    return new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('Can not download artifact. Timeout exceeded')), 30_000);

        got.stream(resourceUrl, {
            headers: {
                Authorization: `OAuth ${teamCityApiToken}`
            },
            https: {
                rejectUnauthorized: false
            }
        })
            .on('error', (error) => reject(new Error(`Can not download artifact: ${error.message}`)))
            .pipe(
                tar
                    .x({
                        cwd: unpackTo,
                        filter: (entryPath) => entryPath.includes(path.basename(PATH_TO_HERMIONE_HTML_REPORT))
                    })
                    .on('error', (error) => reject(new Error(`Can not unpack archive: ${error.message}`)))
                    .on('end', () => {
                        clearTimeout(timer);
                        resolve();
                    })
            );
    });
}
