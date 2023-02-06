import {execSync} from 'child_process';
import {once} from 'events';
import {createReadStream, createWriteStream, promises as fs} from 'fs';
import os from 'os';
import {createInterface} from 'readline';

import {REGION_HEADER, REGION_ISO_CODES} from '@/src/constants';
import {CliUsage, defaultHelpArg} from 'cli/util';
import {loadTestingConfig} from 'config/load-testing';

export interface HandleInput {
    source: string;
    dest: string;
    maxAmmo: number;
    maxLoop: number;
    noUpload?: boolean;
    pickMethod?: string[];
    help?: boolean;
}

export const usage: CliUsage<HandleInput> = {
    parse: {
        source: {type: String, description: 'Путь к файлу из YT'},
        dest: {type: String, description: 'Путь к файлу патронов'},
        maxAmmo: {type: Number, defaultValue: Number.MAX_SAFE_INTEGER, description: 'Максимальное количество патронов'},
        maxLoop: {
            type: Number,
            defaultValue: 0,
            description: 'Максимальное количество повторов одного и того же запроса (`0` — без ограничений)'
        },
        pickMethod: {
            type: String,
            multiple: true,
            optional: true,
            description: 'Формировать патроны только из указанных http методов'
        },
        noUpload: {type: Boolean, optional: true, defaultValue: false, description: 'Не загружать патроны на AWS'},
        help: defaultHelpArg
    },
    options: {helpArg: 'help'}
};

const HEADERS = ['Host: pigeon.lavka.tst.yandex.net', 'User-Agent: YaTank', 'Connection: keep-alive'];

const LUNAPARK_API_URL = 'https://lunapark.yandex-team.ru/api';

let MAX_AMMO: number;
let MAX_LOOP: number;
let REDUCTION_FACTOR: undefined | number = undefined;
let destIx = 0;

export async function handle({source, dest, maxAmmo, maxLoop, noUpload, pickMethod}: HandleInput) {
    MAX_AMMO = maxAmmo;
    MAX_LOOP = maxLoop;

    if (pickMethod) {
        pickMethod = pickMethod.map((method) => method.toUpperCase());
    }

    await fs.writeFile(dest, '');

    const destStream = createWriteStream(dest, {encoding: 'utf8'});

    destStream.once('finish', () => console.log(`Generated ammo total: ${destIx > 0 ? destIx - 1 : 0}`));

    const sourceStream = createReadStream(source, {encoding: 'utf8'});

    const rl = createInterface({
        input: sourceStream,
        crlfDelay: Infinity
    });

    rl.on('line', (line) => {
        const ammo = getAmmo(line, {pickMethod});

        if (ammo) {
            destIx++;
            destStream.write(ammo);
        }
    });

    await once(rl, 'close');
    destStream.end();

    if (!noUpload) {
        uploadAmmoFile(dest);
    }
}

function getAmmo(line: string, {pickMethod}: {pickMethod?: HandleInput['pickMethod']} = {}) {
    if (destIx > MAX_AMMO) {
        return;
    }

    try {
        const {method, url, body, cnt} = JSON.parse(line);

        if (pickMethod && !pickMethod.includes(method.toUpperCase())) {
            return;
        }

        if (url.includes('://')) {
            return;
        }

        let ammo =
            `${method} ${url} HTTP/1.1\r\n` +
            [
                ...HEADERS,
                getRegionHeader(url),
                ...(method === 'POST' ? ['Accept: application/json', 'Content-Type: application/json'] : []),
                ...(body ? [`Content-Length: ${Buffer.byteLength(body, 'utf8')}`] : [])
            ].join('\r\n') +
            '\r\n' +
            (body ? '\r\n' + body : '') +
            '\r\n';
        ammo = `${Buffer.byteLength(ammo, 'utf8')} ${getTag(url)}` + '\r\n' + ammo;

        return Array(handleCount(cnt)).fill(ammo).join('');
    } catch (e) {
        console.error(e);
    }
}

function getRegionHeader(url: string) {
    const returnee = (region: string) => `${REGION_HEADER}: ${region.toUpperCase()}`;

    for (const region of REGION_ISO_CODES) {
        if (startsWith(url, `/${region}/`)) {
            return returnee(region);
        }
    }

    return returnee(REGION_ISO_CODES[0]);
}

function handleCount(origCnt: number) {
    if (!MAX_LOOP) {
        return origCnt;
    }

    if (REDUCTION_FACTOR === undefined) {
        REDUCTION_FACTOR = origCnt / MAX_LOOP;
    }

    return Math.ceil(origCnt / REDUCTION_FACTOR);
}

function getTag(url: string) {
    if (url === '/' || startsWith(url, '/?')) {
        return 'index';
    }

    if (startsWith(url, '/api/v1/attributes')) {
        return 'attributes';
    }

    if (startsWith(url, '/api/v1/front-categories')) {
        return 'front_categories';
    }

    if (startsWith(url, '/api/v1/import')) {
        return 'import';
    }

    if (startsWith(url, '/api/v1/products/search')) {
        return 'search';
    }

    if (startsWith(url, '/api/v1/products')) {
        return 'products';
    }

    if (startsWith(url, '/api')) {
        return 'api';
    }

    if (startsWith(url, '/internal')) {
        return 'internal';
    }

    return 'unknown';
}

function startsWith(str: string, part: string) {
    return part === str.substr(0, part.length);
}

function uploadAmmoFile(file: string) {
    console.log('Uploading the ammo file...');

    const curl = [
        'curl',
        `${LUNAPARK_API_URL}/addammo.json`,
        `-F"login=${os.userInfo().username}"`,
        `-F"dsc=${loadTestingConfig.recordingName}"`,
        `-F"file=@${file}"`
    ].join(' ');

    const result = execSync(curl);

    console.log(`Done: ${result}`);
    console.log('Update the "loadTesting.configData.ammofile" property in the "service.yaml" file');
}
