/**
 * @jest-environment node
 */
import config from '../../../../config';

import Telebot from './telebot';

describe('telebot', () => {
    Telebot(config().telegram);

    test('send', async () => {
        // return telebot.send('test message');
    });
});
