import path from 'path';

import {assertString} from 'service/helper/assert-string';

const FIXTURES_DIR = '__fixtures__';

export function getFixturePath(name: string) {
    const originalPrepareStackTrace = Error.prepareStackTrace;
    Error.prepareStackTrace = (_, stack) => stack;
    const stack = (new Error().stack as unknown) as NodeJS.CallSite[];
    Error.prepareStackTrace = originalPrepareStackTrace;

    const parentModulePath = assertString(stack[1].getFileName());
    const parentModuleSrcDir = path.dirname(parentModulePath).replace('/out', '');
    return path.resolve(parentModuleSrcDir, FIXTURES_DIR, name);
}
