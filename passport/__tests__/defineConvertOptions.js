import defineConvertOptions from '../defineConvertOptions';

describe('defineConvertOptions', () => {
    it('should return object', () => {
        const options = defineConvertOptions();

        expect(typeof options).toBe('object');
    });

    it('should return object with default props: type: "jpeg" & compression: 0.6', () => {
        const options = defineConvertOptions();

        expect(options).toEqual({
            type: 'jpeg',
            compression: 0.6
        });
    });

    it('should return object with prop compression: 0.5 if image is too big', () => {
        const options = defineConvertOptions('jpeg', 6291456);

        expect(options).toEqual({
            type: 'jpeg',
            compression: 0.5
        });
    });

    it('should return object with prop type: "jpeg" if image is greater than 1Mb size and has png type', () => {
        const options = defineConvertOptions('png', 1572864); // 1.5Mb

        expect(options).toEqual({
            type: 'jpeg',
            compression: 0.6
        });
    });
});
