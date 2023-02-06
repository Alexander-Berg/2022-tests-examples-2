import * as extracted from '../banner.js';

describe('Dashboard.Main.Banner', () => {
    it('should call setItem of localStore and call setState', () => {
        const setItem = jest.spyOn(Storage.prototype, 'setItem');
        const obj = {
            setState: jest.fn()
        };

        extracted.closeBanner.call(obj);
        expect(setItem).toHaveBeenCalledTimes(1);
        expect(setItem).toHaveBeenCalledWith('banner', 'anchor');
        expect(obj.setState).toHaveBeenCalledTimes(1);
        expect(obj.setState).toHaveBeenCalledWith({
            toggler: false
        });

        setItem.mockRestore();
    });
});
