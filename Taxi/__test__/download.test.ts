import fs from 'fs';
import nock from 'nock';

import {download} from '../utils';

describe('download', () => {
    const filePath = __dirname + '/replies/test-file.json';
    const host = 'http://test.com';
    const endpoint = '/download';
    const expected = JSON.parse(fs.readFileSync(filePath, {encoding: 'utf8'}));

    nock(host).get(endpoint).replyWithFile(200, filePath).persist();

    test('download to string', async () => {
        const str = await download(host + endpoint);

        expect(JSON.parse(str)).toStrictEqual(expected);
    });

    test('download to file', async () => {
        const destinationPath = __dirname + '/results/test-file.json';
        await download(host + endpoint, destinationPath);

        expect(JSON.parse(fs.readFileSync(destinationPath, {encoding: 'utf8'}))).toStrictEqual(expected);
    });
});
