import {ExecOptions} from 'child_process';

import {execOnChanged, retry} from '../../common/utils';
import {getStableSHA} from './utils';

// перезапускаем тесты в случае ошибки, на случай флапающих тестов
export default retry(async (options: ExecOptions) => {
    await execOnChanged('"npm run test"', await getStableSHA());
}, 2);
