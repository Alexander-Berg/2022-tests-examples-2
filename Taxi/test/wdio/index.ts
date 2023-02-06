import type {Options} from '@wdio/types';

import {capabilityConfig} from './capability';
import {hooksConfig} from './hooks';
import {specsConfig} from './specs';
import {typescriptConfig} from './typescript';

export const config: Options.Testrunner = {
    ...typescriptConfig,
    ...capabilityConfig,
    ...specsConfig,
    ...hooksConfig,
};
