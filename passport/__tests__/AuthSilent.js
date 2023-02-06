import React from 'react';
import {shallow} from 'enzyme';
import {Button} from '@components/Button';
import {AuthSilent} from '../AuthSilent';
import {magicService} from '../../magicService';

jest.mock('../../magicService', () => ({
    magicService: {
        init: jest.fn(),
        start: jest.fn(),
        stop: jest.fn()
    }
}));

jest.useFakeTimers();

describe('AuthSilent', () => {
    describe('AuthSilent component', () => {
        let openOrig;

        let locationOrig;

        const getProps = (props = {}) => ({
            csrfToken: 'FJKEFE',
            trackId: 'IOUIUEGF',
            retpath: 'someUrl',
            ...props
        });

        beforeAll(() => {
            openOrig = global.window.open;
            global.window.open = jest.fn();
            locationOrig = window.location;
        });
        afterAll(() => {
            global.window.open = openOrig;
            delete window.location;
            window.location = locationOrig;
        });
        beforeEach(() => {
            delete window.location;
            window.location = {
                href: '',
                protocol: 'https:',
                hostname: 'test.test'
            };
            global.window.open.mockReset();
            magicService.init.mockReset();
            magicService.start.mockReset();
            magicService.stop.mockReset();
        });
        it('Should render Button on start', () => {
            const props = getProps();
            const authSilentComponent = shallow(<AuthSilent {...props} />);

            expect(authSilentComponent.find(Button).length).toBe(1);
        });
    });
});
