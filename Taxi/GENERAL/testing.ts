import {Presets} from 'express-yandex-csp';

import defaultConfig from './defaults';
import apiTestingCspPreset from './presets/api-testing';
import mdsTestingCspPreset from './presets/mds-testing';
import staticSelfCspPreset from './presets/static-self';

const presets: Presets = [
    ...defaultConfig,
    apiTestingCspPreset,
    mdsTestingCspPreset,
    staticSelfCspPreset,
];

export default presets;
