import {push} from 'react-router-redux';

import {setEditMode} from '../../../../common/actions';
import {
    EDIT_MODE_ADDRESSES,
    EDIT_MODE_DELIVERY_ADDRESSES,
    ADDRESSES_LINK,
    setAddressesEditMode
} from '../../../addresses/actions';

import * as extracted from '../addresses_block.js';

jest.mock('../../../../common/actions', () => ({
    setEditMode: jest.fn()
}));

jest.mock('../../../addresses/actions', () => ({
    setAddressesEditMode: jest.fn()
}));

jest.mock('react-router-redux', () => ({
    push: jest.fn()
}));

describe('Morda.AddressesBlock', () => {
    describe('getAddressLink', () => {
        it('should return desktop link', () => {
            const props = extracted.getAddressLink.call({
                isTouch: false
            }).props;

            expect(props.pseudo).toBeTruthy();
            expect(props.url).toBe(undefined);
        });
        it('should return mobile link', () => {
            const props = extracted.getAddressLink.call({
                isTouch: true
            }).props;

            expect(props.pseudo).toBeFalsy();
            expect(props.url).toBe(ADDRESSES_LINK);
        });
    });
    describe('showAddresses', () => {
        it('should call setEditMode', () => {
            const obj = {
                setEditMode: jest.fn()
            };

            extracted.showAddresses.call(obj);
            expect(obj.setEditMode).toHaveBeenCalledTimes(1);
            expect(obj.setEditMode).toHaveBeenCalledWith(EDIT_MODE_ADDRESSES);
        });
        it('should call preventDefault', () => {
            const obj = {
                setEditMode: jest.fn()
            };
            const event = {
                preventDefault: jest.fn()
            };

            extracted.showAddresses.call(obj, event);
            expect(event.preventDefault).toHaveBeenCalledTimes(1);
        });
    });
    describe('showDeliveryAddresses', () => {
        it('should call setEditMode', () => {
            const obj = {
                setEditMode: jest.fn()
            };

            extracted.showDeliveryAddresses.call(obj);
            expect(obj.setEditMode).toHaveBeenCalledTimes(1);
            expect(obj.setEditMode).toHaveBeenCalledWith(EDIT_MODE_DELIVERY_ADDRESSES);
        });
        it('should call preventDefault', () => {
            const obj = {
                setEditMode: jest.fn()
            };
            const event = {
                preventDefault: jest.fn()
            };

            extracted.showDeliveryAddresses.call(obj, event);
            expect(event.preventDefault).toHaveBeenCalledTimes(1);
        });
    });
    describe('setMode', () => {
        let obj = null;

        beforeEach(() => {
            obj = {
                props: {
                    dispatch: jest.fn()
                }
            };
        });
        afterEach(() => {
            setEditMode.mockClear();
            setAddressesEditMode.mockClear();
        });
        it('should dispatch setAddressesEditMode and setEditMode', () => {
            const mode = 'mode';

            extracted.setMode.call(obj, mode);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(setAddressesEditMode).toHaveBeenCalledTimes(1);
            expect(setAddressesEditMode).toHaveBeenCalledWith(mode);
            expect(setEditMode).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledWith(mode);
        });
        it('should dispatch setAddressesEditMode and push', () => {
            const mode = 'mode';

            obj.isTouch = true;

            extracted.setMode.call(obj, mode);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(setAddressesEditMode).toHaveBeenCalledTimes(1);
            expect(setAddressesEditMode).toHaveBeenCalledWith(mode);
            expect(push).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledWith(ADDRESSES_LINK);
        });
    });
});
