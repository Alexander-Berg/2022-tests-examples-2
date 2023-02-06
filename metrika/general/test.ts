import { omit } from 'lodash';
import * as rawDevConfig from './development';

module.exports = omit(rawDevConfig, 'default');
