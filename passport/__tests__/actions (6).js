import * as actions from '../actions';

describe('Morda.Devices.actions', () => {
    test('saveAvatarInitialTrack', () => {
        const list = 'value';

        expect(actions.getDevicesTokens(list)).toEqual({
            type: actions.GET_TOKENS_BY_DEVICE,
            list
        });
    });
    test('updateTokenTab', () => {
        const tokenType = 'value';
        const id = 'value';

        expect(actions.updateTokenTab(id, tokenType)).toEqual({
            type: actions.UPDATE_DEVICE_TOKEN_TAB,
            tokenType,
            id
        });
    });
    test('showDisablingTokens', () => {
        const info = 'value';

        expect(actions.showDisablingTokens(info)).toEqual({
            type: actions.SHOW_DISABLING_TOKENS,
            info
        });
    });
    test('updateListToDisable', () => {
        const info = 'value';

        expect(actions.updateListToDisable(info)).toEqual({
            type: actions.UPDATE_DISABLE_LIST,
            info
        });
    });
    test('updateDevicesListToDisable', () => {
        const idList = 'value';

        expect(actions.updateDevicesListToDisable(idList)).toEqual({
            type: actions.UPDATE_DEVICES_DISABLE_LIST,
            idList
        });
    });
    test('showDevicesWithSameName', () => {
        const idList = 'value';
        const deviceName = 'value';

        expect(actions.showDevicesWithSameName(idList, deviceName)).toEqual({
            type: actions.SHOW_SAME_NAME_DEVICES,
            deviceName,
            idList
        });
    });
});
