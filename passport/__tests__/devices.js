import {push} from 'react-router-redux';

import {setEditMode} from '../../../../common/actions';
import {getDevicesList} from '../../../devices';

import * as extracted from '../devices.js';

jest.mock('react-router-redux', () => ({
    push: jest.fn()
}));
jest.mock('../../../../common/actions', () => ({
    setEditMode: jest.fn()
}));
jest.mock('../../../devices', () => ({
    getDevicesList: jest.fn()
}));

describe('Morda.HistoryBlock.Devices', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            props: {
                settings: {
                    isTouch: false
                },
                dispatch: jest.fn()
            }
        };
    });
    afterEach(() => {
        getDevicesList.mockClear();
    });

    describe('onLinkClick', () => {
        it('should dispatch getDevicesList and setEditMode', () => {
            extracted.onLinkClick.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(getDevicesList).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledWith('devices-list');
        });
        it('should dispatch getDevicesList and push', () => {
            obj.props.settings.isTouch = true;

            extracted.onLinkClick.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(getDevicesList).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledWith('/profile/devices');
        });
    });
});
