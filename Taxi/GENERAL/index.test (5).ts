/**
 * @jest-environment node
 */
import Bottle from 'bottlejs';

import config from '../../../config';
import {CONFIG, TELEGRAM} from '..';

import Telegram from './';

describe('telebot', () => {
    const bottle = new Bottle();
    bottle.constant(CONFIG, config);
    bottle.factory(TELEGRAM, Telegram);

    test('send some message', async () => {
        // return bottle.container[TELEGRAM].send('Test message 2');
    });
});
