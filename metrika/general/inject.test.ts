/**
 * Подмена основного модуля для unit тестов
 */
import { BuildFlags } from '@mappings/mapping';
import { ArgOptions } from '@mappings/utils';
import {
    features,
    DEBUG_FEATURE,
    BRO_FEATURE,
    ASSESSOR_FEATURE,
    SUPER_DEBUG_FEATURE,
} from '@generated/features';

const excludedFeatures = [
    BRO_FEATURE,
    DEBUG_FEATURE,
    ASSESSOR_FEATURE,
    SUPER_DEBUG_FEATURE,
];

if (typeof global !== 'undefined' && (global as any).window) {
    (global as any).window.Promise = Promise;
}

const flags: Readonly<BuildFlags> = features
    .filter((feature) => !excludedFeatures.includes(feature))
    .reduce((acc, feature) => {
        acc[feature] = true;
        return acc;
    }, {} as any as BuildFlags);
let args = {};
try {
    args = JSON.parse(process.env.ARG_OPTIONS || '');
} catch (e) {
    // empty
}
const argOptions: Readonly<ArgOptions> = Object.assign(args, {
    version: 'unitTest',
}) as any;

export const resourceId = 'unit.js';

export { flags, argOptions };
