import { omit } from 'lodash';

/* eslint-disable-next-line import/namespace */
import * as rawDevConfig from './development';

module.exports = omit(rawDevConfig, 'default');
