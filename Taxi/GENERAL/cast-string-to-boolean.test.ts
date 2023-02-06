import {describe, expect, it} from 'tests/jest.globals';

import castStringToBoolean from 'service/info-model-import/cast-string-to-boolean';

describe('cast string to boolean', () => {
    it.each(['да', 'yes', '1', 'иСтИнА', 'true', '  t  ', 1])('should cast "%s" to "true"', (value) => {
        expect(castStringToBoolean(value)).toBeTruthy();
    });

    it.each(['нет', 'no', '0', 'лОжЬ', 'false', '  f  ', 0])('should cast "%s" to "false"', (value) => {
        expect(castStringToBoolean(value)).toBeFalsy();
    });

    it.each([100500, 'qwerty', '01'])('should return "undefined" for value "%s"', (value) => {
        expect(castStringToBoolean(value)).toBeUndefined();
    });
});
