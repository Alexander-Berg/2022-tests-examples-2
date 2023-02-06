import {Presets} from 'express-yandex-csp';

import defaultConfig from './defaults';
import apiTestingCspPreset from './presets/api-testing';
import staticSelfCspPreset from './presets/static-self';

const presets: Presets = [
    ...defaultConfig,
    apiTestingCspPreset,
    staticSelfCspPreset,
];

export default presets;
