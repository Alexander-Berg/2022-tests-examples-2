import './non-module';
import { func, someVar } from './lib';
import abc from './defaultFunc';
import abc2 from './defaultVar';
const val = func() + ' ' + abc();
const val2 = someVar + ' ' + abc2();

export function instantRunResult() {
    return val + '\n' + val2;
}

export function runFuncExport() {
    return func() + ' ' + abc();
}

export function runVarExport() {
    return someVar + ' ' + abc2();
}
