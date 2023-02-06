import 'core-js';
import 'regenerator-runtime';

import {configure} from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

configure({adapter: new Adapter()});

jest.mock('popper.js', () => {
    const PopperJS = jest.requireActual('popper.js');
    return class {
        static placements = PopperJS.placements;
        constructor() {
            return {
                destroy: () => {},
                scheduleUpdate: () => {},
            };
        }
    };
});

global.window.__CORP_CLIENT = {
    config: {
        lang: 'ru',
    },
};
