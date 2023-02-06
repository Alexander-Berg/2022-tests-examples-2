import {assertString} from 'service/helper/assert-string';

export default function buildServerUrl(path: string, port: number) {
    const domain = assertString(process.env.TEST_DOMAIN);
    const url = new URL(path, [domain, port].join(':'));
    return url.href;
}
