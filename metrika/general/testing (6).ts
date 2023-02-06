import { Presets } from 'express-yandex-csp';

import defaultConfig from './defaults';
import mdsTestingCspPreset from './presets/mds-testing';
import passportCspPreset from './presets/passport';
import sentryTestingCspPreset from './presets/sentry-testing';

const presets: Presets = [
    ...defaultConfig,
    mdsTestingCspPreset,
    passportCspPreset,
    sentryTestingCspPreset,
];

export default presets;
