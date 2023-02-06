import i18n from '_pkg/utils/localization/i18n';
import {showTimeFull} from '../showTimeFull';

const RESULT = 'result string';

jest.mock('_pkg/utils/localization/i18n');

(i18n.print as jest.Mock).mockReturnValue(RESULT);

describe('utils/strict/showTimeFull', () => {
    beforeEach(() => {
        jest.fn(i18n.print).mockReset();
    });

    test('showTimeFull without sec', () => {
        expect(showTimeFull()).toEqual('');

        expect(i18n.print).not.toHaveBeenCalled();
    });

    test('showTimeFull 0 sec', () => {
        expect(showTimeFull(0)).toEqual(RESULT);

        expect(i18n.print).toHaveBeenCalledWith('seconds_template', {
            placeholder: {
                param1: 0
            }
        });
    });

    test('showTimeFull 30 sec', () => {
        expect(showTimeFull(30)).toEqual(RESULT);

        expect(i18n.print).toHaveBeenCalledWith('seconds_template', {
            placeholder: {
                param1: 30
            }
        });
    });

    test('showTimeFull 60 sec', () => {
        expect(showTimeFull(60)).toEqual(RESULT);

        expect(i18n.print).toHaveBeenCalledWith('minutes_seconds_template', {
            placeholder: {
                param1: 1,
                param2: 0
            }
        });
    });

    test('showTimeFull 60030 sec', () => {
        expect(showTimeFull(60030)).toEqual(RESULT);

        expect(i18n.print).toHaveBeenCalledWith('minutes_seconds_template', {
            placeholder: {
                param1: 1000,
                param2: 30
            }
        });
    });
});
