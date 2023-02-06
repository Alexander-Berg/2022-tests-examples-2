import {Config} from './types';

export default (defaultConfig: Config) => ({
    ...defaultConfig,
    env: 'test'
});
