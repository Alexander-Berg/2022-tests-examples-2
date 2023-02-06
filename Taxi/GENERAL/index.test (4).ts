/**
 * @jest-environment node
 */
import config from '../../../../config';

import Tanker from './index';

describe('tanker', () => {
    config();
    const tanker = Tanker();

    test('getKeysets', async () => {
        return (
            tanker
                .getKeysets('taxi', 'master')
                // .then(result => console.error('tanker result', result))
                /* eslint-disable-next-line no-console */
                .catch(err => console.info(err))
        );
    });
    test('getKeyset', async () => {
        return (
            tanker
                .getKeyset('taxi', 'master', 'corp-client')
                // .then(result => console.error('tanker result', result))
                /* eslint-disable-next-line no-console */
                .catch(err => console.info(err))
        );
    });
    test('export', async () => {
        return (
            tanker
                .export('taxi', 'master', 'corp-client')
                // .then(result => console.error('tanker result', result))
                /* eslint-disable-next-line no-console */
                .catch(err => console.info(err))
        );
    });
});
