import processErrors from '../processErrors';

describe('processErrors', () => {
    it('should return error text as a string', () => {
        const result = processErrors('display_name.empty');

        expect(typeof result).toBe('string');
    });

    it('should handle with array arguments', () => {
        const result = processErrors(['display_name.empty', 'some random shit']);

        expect(result).toBe(i18n('_AUTH_.displayname_errors_missingvalue'));
    });

    it('should handle with string arguments', () => {
        const result = processErrors('display_name.empty');

        expect(result).toBe(i18n('_AUTH_.displayname_errors_missingvalue'));
    });

    it('should handle with empty arguments', () => {
        const result = processErrors();

        expect(result).toBe(i18n('_AUTH_.avatar.error-internal'));
    });
});
