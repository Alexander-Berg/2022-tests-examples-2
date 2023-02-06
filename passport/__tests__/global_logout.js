import * as extracted from '../global_logout.js';

describe('Morda.HistoryBlock.GlobalLogout', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            setState: jest.fn()
        };
    });
    describe('closeAlert', () => {
        it('should call setState', () => {
            extracted.closeAlert.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({
                isModalOpened: false
            });
        });
    });
    describe('showAlert', () => {
        it('should call setState and preventDefault of event', () => {
            const event = {
                preventDefault: jest.fn()
            };

            extracted.showAlert.call(obj, event);
            expect(event.preventDefault).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({
                isModalOpened: true
            });
        });
    });
});
