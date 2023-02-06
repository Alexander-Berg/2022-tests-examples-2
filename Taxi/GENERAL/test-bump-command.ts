import {CliUsage, defaultHelpArg} from '@lavka-js-toolbox/cli';
import {getPackages} from '@lerna/project';

import {Changelog} from './changelog';
import {config} from './config';
import {getDependencyAffectedPackages, getPackageUsages, sortPackagesByDependencies} from './monorepo';

interface HandleInput {
    affected: string[];
    help?: boolean;
}

export const usage: CliUsage<HandleInput> = {
    parse: {
        affected: {type: String, multiple: true, alias: 'a', description: 'Names of affected packages'},
        help: defaultHelpArg
    },
    options: {
        helpArg: 'help',
        headerContentSections: [{content: 'Compile packages'}]
    }
};

export async function handle({affected}: HandleInput) {
    affected = affected.map((name) => `${config.npm.scope}/${name}`);
    console.log(`Affected:${affected.reduce((acc, name) => acc + '\n\t- ' + name, '')}`);

    const packages = sortPackagesByDependencies(await getPackages());

    for (const pkgName of affected) {
        if (!packages.some(({name}) => pkgName === name)) {
            throw new Error(`Invalid package name: "${pkgName}"`);
        }
    }

    const affectedNames = new Set(affected);
    const affectedPackages: LernaPackage[] = [];
    for (const pkg of packages) {
        if (affectedNames.has(pkg.name)) {
            affectedPackages.push(pkg);
            console.log(`\nAffected "${pkg.name}" package usages:`);
            console.log(JSON.stringify(getPackageUsages(pkg.name, packages), null, 4));
        }
    }

    const depAffected = getDependencyAffectedPackages(affectedPackages, packages);

    const changelog = new Changelog(affectedPackages, depAffected);
    changelog.setHeaders({version: 'test-bump', revision: 'test-bump'});
    console.log('\n' + changelog.getChangelog());
}
