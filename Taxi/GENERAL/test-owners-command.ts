import {CliUsage, defaultHelpArg} from '@lavka-js-toolbox/cli';
import {getVersionValues} from '@lavka-js-toolbox/vault';
import execa from 'execa';
import {isEmpty} from 'lodash';
import pMap from 'p-map';

import {config} from '../config';
import {logInToNpm} from '../monorepo';
import {BIN_LERNA, getNpmCacheSlug, isCi} from '../util';

interface HandleInput {
    fix?: boolean;
    help?: boolean;
}

export const usage: CliUsage<HandleInput> = {
    parse: {
        fix: {type: Boolean, optional: true, description: 'Fix owners'},
        help: defaultHelpArg
    },
    options: {
        helpArg: 'help',
        headerContentSections: [{content: 'Test npm owners of packages'}]
    }
};

export async function handle({fix}: HandleInput = {}) {
    const {errors, hasValidOwners} = validatePackageOwners(await getRawOwners());

    console.log({hasValidOwners});

    if (errors) {
        console.error('Invalid npm owners of packages', errors);

        if (fix) {
            await fixOwners();
        } else {
            process.exit(1);
        }
    }
}

async function getRawOwners() {
    const {stdout} = await execa(BIN_LERNA, ['exec', '--parallel', '--', 'npm', 'owner', getNpmCacheSlug(), 'ls'], {
        stderr: 'inherit'
    });

    return stdout.split('\n');
}

function validatePackageOwners(rawOwners: string[]) {
    const errors: Record<string, string[]> = {};
    const hasValidOwners = new Set<string>();

    rawOwners.forEach((str) => {
        const {packageName, owner} = parseOwner(str);
        if (config.npm.owners.includes(owner)) {
            hasValidOwners.add(packageName);
        } else {
            errors[packageName] ||= [];
            errors[packageName].push(owner);
        }
    });

    return {
        hasValidOwners: [...hasValidOwners].sort(),
        ...(!isEmpty(errors) ? {errors} : {})
    };
}

function parseOwner(str: string) {
    const matches = str.matchAll(new RegExp(`${config.npm.scope}/([^:]+): ([^<]+)<.+`, 'g'));
    const [_, packageName, owner] = [...matches][0];
    return {packageName, owner: owner.trim()};
}

async function fixOwners() {
    if (isCi()) {
        const secrets = await getVersionValues(config.yav_secret, ['npm-token']);
        await logInToNpm({username: config.robot, password: secrets['npm-token']});
    }

    await pMap(config.npm.owners, (owner) =>
        execa(BIN_LERNA, ['exec', '--parallel', '--', 'npm', 'owner', 'add', getNpmCacheSlug(), owner], {
            stdout: 'inherit',
            stderr: 'inherit'
        })
    );

    const {errors, hasValidOwners} = validatePackageOwners(await getRawOwners());

    await pMap(hasValidOwners, async (packageName) => {
        const invalidOwners = errors?.[packageName];
        if (Array.isArray(invalidOwners)) {
            console.log({packageName, invalidOwners});
            await pMap(invalidOwners, (owner) =>
                execa('npm', ['owner', 'rm', getNpmCacheSlug(), owner, `${config.npm.scope}/${packageName}`], {
                    stdout: 'inherit',
                    stderr: 'inherit'
                })
            );
        }
    });
}
