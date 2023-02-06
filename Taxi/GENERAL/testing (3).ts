import {Presets} from 'express-yandex-csp';

import defaultConfig from './defaults';
import apiTestingCspPreset from './presets/api-testing';
import frameTestingCspPreset from './presets/frame-testing';
import mdsTestingCspPreset from './presets/mds-testing';
import passportCspPreset from './presets/passport';
import staticSelfCspPreset from './presets/static-self';

const presets: Presets = [
    ...defaultConfig,
    mdsTestingCspPreset,
    passportCspPreset,
    apiTestingCspPreset,
    staticSelfCspPreset,
    frameTestingCspPreset,
];

export default presets;
