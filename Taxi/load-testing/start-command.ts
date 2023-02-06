import {appendIssueComment, createClient, Issue, searchIssues, Session} from '@lavka-js-toolbox/startrek';
import Sandbox from '@yandex-int/sandboxer';
import {getCert} from '@yandex-int/yandex-internal-cert';
import assert from 'assert';
import {appendFileSync, existsSync, readFileSync, unlinkSync, writeFileSync} from 'fs';
import got from 'got';
import {load as parseYaml} from 'js-yaml';
import {get as getByPath, template} from 'lodash';
import {join as joinPath} from 'path';

import {ROBOT_PIGEON} from '@/src/constants';
import type {User} from '@/src/entities/user/entity';
import {CliUsage, defaultHelpArg} from 'cli/util';
import {baseDir} from 'config/load-testing';
import {config, env, isDevelopment} from 'service/cfg';
import {dump, getLatestMigrationVersion, grantPrivileges, pgmigtate, roll} from 'service/db/dump-utils';
import {assertString} from 'service/helper/assert-string';
import {measureExecution} from 'service/helper/create-ms-timer';
import {delayMs} from 'service/helper/delay';
import {ImportTester} from 'service/import/tester';

export interface HandleInput {
    fromStep?: number;
    noIssueComment?: boolean;
    issueKey?: string;
    help?: boolean;
}

type StepHandlerInput = {
    comments: string[];
    issue: Issue;
    payload: {
        user?: User;
    };
};

export const usage: CliUsage<HandleInput> = {
    parse: {
        fromStep: {type: Number, optional: true, description: 'Начиная с указанного шага'},
        noIssueComment: {type: Boolean, optional: true, description: 'Не отбивать комментарии в задачу'},
        issueKey: {type: String, optional: true, description: 'Номер задачи для отбивки выполнения'},
        help: defaultHelpArg
    },
    options: {helpArg: 'help'}
};

const SERVICE_YAML = joinPath(process.cwd(), 'service.yaml');
const STATE_FILE = joinPath(process.cwd(), baseDir, '.state');
const LOG_FILE = joinPath(process.cwd(), baseDir, 'start.log');
const DB_DUMP = joinPath(process.cwd(), baseDir, 'db.dump');
const REGION_ISO_CODE = 'RU';
const LUNAPARK_URL = 'https://lunapark.yandex-team.ru';
const NANNY_API_URL = 'https://nanny.yandex-team.ru/v2';

const IMPORT_ROWS = 10000;
const ATTRIBUTES_COUNT = 1;

const STARTREK = {
    TOKEN: assertString(process.env.STARTREK_TOKEN),
    QUEUE: 'TAXIREL',
    COMPONENT_ID: 105070,
    FIND_DELAY: 30000,
    FIND_ATTEMPTS: 40
};

const SANDBOX = {
    TOKEN: assertString(process.env.SANDBOX_TOKEN),
    TASK_TYPE: 'FIRESTARTER',
    OWNER: 'LAVKASERVICES'
};

const STATE = {
    INITIALIZED: 'INITIALIZED',
    ERROR: 'ERROR',
    IN_PROGRESS: 'IN_PROGRESS',
    COMPLETED: 'COMPLETED'
};

const STEPS = [
    {
        handler: prepareDatabase,
        message: 'Prepare database'
    },
    {
        handler: testImport,
        message: 'Test import'
    },
    {
        handler: startShooting,
        message: 'Shooting via Lunapark Firestarter'
    }
];

export async function handle({fromStep = 0, noIssueComment = false, issueKey}: HandleInput) {
    log('Load testing initialized');

    if (isDevelopment && existsSync(STATE_FILE)) {
        unlinkSync(STATE_FILE);
    }

    assertState(STATE.INITIALIZED);

    const {issue, payload} = await prepare(issueKey);

    const publishComment = async ({issue, comment}: {issue: Issue; comment: string}) => {
        comment = `**${env}** ${comment}`;

        if (noIssueComment) {
            console.log(`\n=== ISSUE COMMENT ===\n${comment}\n`);
        } else {
            await appendIssueComment({issue, comment});
        }
    };

    try {
        await publishComment({issue, comment: 'Starting auto-load'});
        setState(STATE.IN_PROGRESS);

        for (let i = 0; i < STEPS.length; i++) {
            const {handler, message} = STEPS[i];

            if (fromStep > i + 1) {
                log(`Skipping step ${i + 1}: ${message}`);
                continue;
            }

            const comments = [`Load testing [**step ${i + 1}** of **${STEPS.length}**]:`, message];

            await handler({comments, issue, payload});
            await publishComment({issue, comment: comments.join('\n')});
        }

        setState(STATE.COMPLETED);
    } catch (e) {
        log(e);
        setState(STATE.ERROR);
        await publishComment({issue, comment: `Error occurred: ${String(e)}`});
        throw e;
    }
}

async function prepare(issueKey: HandleInput['issueKey']) {
    try {
        const session = createClient().createSession({token: STARTREK.TOKEN});
        const issue = await findReleaseTicket(session, issueKey);
        const payload: StepHandlerInput['payload'] = {};

        log(`Found issue: "${issue.getKey()}: ${issue.getSummary()}"`);

        return {session, issue, payload};
    } catch (e) {
        log(e);
        setState(STATE.ERROR);
        throw e;
    }
}

async function findReleaseTicket(session: Session, issueKey?: string) {
    const query = issueKey
        ? {filter: {key: issueKey}}
        : {
              filter: {
                  queue: STARTREK.QUEUE,
                  components: STARTREK.COMPONENT_ID,
                  status: 'open'
              }
          };

    const find = async () => {
        for await (const {issue} of searchIssues(session, query)) {
            return issue;
        }
    };

    for (let i = 0; i < STARTREK.FIND_ATTEMPTS; i++) {
        log(`Attempt to find release ticket [${i + 1}/${STARTREK.FIND_ATTEMPTS}]`);
        const issue = await find();
        if (issue) {
            return issue;
        }
        await delayMs(STARTREK.FIND_DELAY);
    }

    throw new Error('Unable to find release ticket');
}

async function prepareDatabase({comments}: StepHandlerInput) {
    if (!existsSync(DB_DUMP)) {
        const dumpCreds = config.db.readOnlyProduction;

        assert(dumpCreds, 'No dump credentials provided!');

        log(`Starting dump to: "${DB_DUMP}"`);
        const ms = await measureExecution(() => dump(dumpCreds, DB_DUMP));
        log(`Dump completed in ${(ms / 1000).toFixed(2)} seconds`, {comments});
    } else {
        log(`Dump file already exists: "${DB_DUMP}"`);
    }

    const latestMigrationBeforeRestore = await getLatestMigrationVersion();

    log(`Rolling database dump: "${DB_DUMP}"`);
    const ms = await measureExecution(async () => {
        await roll(DB_DUMP, ['-n public', '-n catalog', '--verbose']);

        if (!isDevelopment) {
            await grantPrivileges();
        }
    });
    log(`Roll completed in ${(ms / 1000).toFixed(2)} seconds`, {comments});

    await pgmigtate(latestMigrationBeforeRestore);
    log(`Migrations has been applied from ${latestMigrationBeforeRestore} version`, {comments});
}

async function testImport({comments, payload}: StepHandlerInput) {
    const insertCount = Math.ceil(IMPORT_ROWS / 2);
    const updateCount = IMPORT_ROWS - insertCount;

    const tester = new ImportTester({
        userLogin: ROBOT_PIGEON,
        regionIsoCode: REGION_ISO_CODE,
        attributesCount: ATTRIBUTES_COUNT
    });
    await tester.ready;

    payload.user = tester.getUser();

    comments.push(`Total info model attributes: ${tester.countInfoModelAttributes()}`);

    let ms = await measureExecution(() => tester.generateInsertEntries({count: insertCount}));
    log(`Generated ${insertCount} rows to insert in ${(ms / 1000).toFixed(2)} seconds`);

    ms = await measureExecution(() => tester.generateUpdateEntries({count: updateCount}));
    log(`Generated ${updateCount} rows to update in ${(ms / 1000).toFixed(2)} seconds`);

    await tester.dispatchEntries();

    log('Committing import');

    ms = await measureExecution(() => tester.commit());
    const dimension = [IMPORT_ROWS, tester.countInfoModelAttributes()].join('x');
    const totalCells = IMPORT_ROWS * tester.countInfoModelAttributes();
    log(`Import completed in ${(ms / 1000).toFixed(2)} seconds`, {comments});
    log(`Total cells: ${dimension} = ${totalCells}`, {comments});
}

async function startShooting({comments, issue}: StepHandlerInput) {
    let result: string;

    try {
        const task = await runFirestarterSandboxTask(issue.getKey());
        log(`Sandbox task "${task.id}" completed`);
        const lunaparkId = task.raw.output_parameters.lunapark_id;
        log(`Lunapark ID: ${lunaparkId}`);
        result = `Shooting started\n${LUNAPARK_URL}/${lunaparkId}`;
    } catch (e) {
        result = `Shooting error occurred\n${String(e)}`;
    }

    log(result, {comments});
}

async function runFirestarterSandboxTask(issueKey: string) {
    const serviceYaml = parseYaml(readFileSync(SERVICE_YAML, {encoding: 'utf8'}));
    const configTemplatePath = getByPath(serviceYaml, 'loadTesting.configTemplate');
    const configTemplate = readFileSync(configTemplatePath, {encoding: 'utf8'});
    const configData = getByPath(serviceYaml, 'loadTesting.configData', {});
    const addressByNannyServiceId = getByPath(serviceYaml, 'loadTesting.addressByNannyServiceId');

    if (addressByNannyServiceId) {
        const address = await getTankAddressByNannyServiceId(addressByNannyServiceId);
        log(`Overriding "loadTesting.configData.address" with "${address}"`);
        configData.address = address;
    }

    const sandbox = new Sandbox({token: SANDBOX.TOKEN});

    const task = await sandbox.task.createDraft({
        owner: SANDBOX.OWNER,
        type: SANDBOX.TASK_TYPE,
        requirements: {},
        description: 'lavka-pigeon: auto-load',
        kill_timeout: 60, // seconds
        tags: ['autoload', 'lavka-pigeon']
    });

    log(`Sandbox draft "${task.id}" created`);

    const params = {
        dry_run: false,
        tank_config: template(configTemplate)({...configData, task: issueKey}),
        use_last_binary: true
    };

    await sandbox.task.updateParameters(
        task.id,
        Object.entries(params).map(([name, value]) => ({name, value}))
    );
    await sandbox.task.startById(task.id);

    log(`Sandbox task "${task.id}" started`);

    return waitSandboxTask(sandbox, task.id);
}

function log(msg: unknown, {comments}: {comments?: string[]} = {}) {
    const entry = `[${new Date().toISOString()}] ${String(msg)}`;

    appendFileSync(LOG_FILE, entry + '\n');

    if (isDevelopment) {
        console.log(entry);
    }

    comments?.push(String(msg));
}

function setState(state: string) {
    writeFileSync(STATE_FILE, state);
}

function getState() {
    if (!existsSync(STATE_FILE)) {
        setState(STATE.INITIALIZED);
    }
    return readFileSync(STATE_FILE, {encoding: 'utf8'}).trim();
}

function assertState(expectedState: string) {
    const state = getState();
    assert(state === expectedState, `Invalid state "${state}", expected: "${expectedState}"`);
}

async function waitSandboxTask(sandbox: Sandbox, taskId: number, {maxAttempts = 30, delay = 5000} = {}) {
    const TASK_STATUS = {
        SUCCESS: 'SUCCESS',
        EXCEPTION: 'EXCEPTION',
        STOPPED: 'STOPPED'
    };

    let counter = 0;

    while (counter < maxAttempts) {
        counter++;

        log(`Checking sandbox task "${taskId}" [${counter}/${maxAttempts}]`);

        const processingTask = await sandbox.task.load(taskId);
        const taskAudit = await processingTask.audit();
        const taskAuditStatuses = JSON.parse(taskAudit.toString());
        const lastStatus = taskAuditStatuses[taskAuditStatuses.length - 1].status;

        if (lastStatus === TASK_STATUS.SUCCESS) {
            return processingTask;
        } else if ([TASK_STATUS.EXCEPTION, TASK_STATUS.STOPPED].includes(lastStatus)) {
            throw new Error(`Sandbox task "${taskId}" failed: ${lastStatus}`);
        }

        await delayMs(delay);
    }

    throw new Error(`The task "${taskId}" takes too long`);
}

async function getTankAddressByNannyServiceId(serviceId: string) {
    const {body} = await got.get(`${NANNY_API_URL}/services/${serviceId}/current_state/instances/`, {
        https: {certificateAuthority: getCert()}
    });
    const address = getByPath(JSON.parse(body), 'result.0.container_hostname');

    if (!address) {
        throw new Error(`Unexpected Nanny Api Response: ${body}`);
    }

    return address;
}
