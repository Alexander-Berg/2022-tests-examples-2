import {AwsClient} from '@lavka-js-toolbox/s3-provider';
import assert from 'assert';
import {existsSync, unlinkSync} from 'fs';
import {join as joinPath} from 'path';

import {CliUsage, defaultHelpArg} from 'cli/util';
import {loadTestingConfig} from 'config/load-testing';

interface HandleInput {
    help?: boolean;
}

export const usage: CliUsage<HandleInput> = {
    parse: {
        help: defaultHelpArg
    },
    options: {helpArg: 'help'}
};

export async function handle() {
    const client = new AwsClient({
        host: loadTestingConfig.awsClient.host,
        bucket: loadTestingConfig.awsClient.bucket,
        key: loadTestingConfig.awsClient.key,
        secret: loadTestingConfig.awsClient.secret
    });

    const dir = joinPath(loadTestingConfig.artifactsDir, loadTestingConfig.recordingName);

    for await (const {
        item: {key}
    } of client.listObjects({prefix: loadTestingConfig.awsClient.prefix + '/'})) {
        const file = key.split('/').pop();
        assert(file, `Invalid AWS object key: ${key}`);

        console.log(`Removing ${file}`);

        await client.dropObject({key});

        const filePath = joinPath(dir, file);
        if (existsSync(filePath)) {
            unlinkSync(filePath);
        }
    }
}
