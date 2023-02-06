import { Presets } from 'express-yandex-csp';

import { presets as defaultPresets } from './defaults';

import { passportCspPreset } from '@metrika/server/csp/presets/passport';

const presets: Presets = [...defaultPresets, passportCspPreset];

export { presets };
