import {DivCustomBlock} from '../../src';

describe('Custom tests', (): void => {
    it('should create simple custom block', (): void => {
        const customBlock = new DivCustomBlock({
            custom_type: 'test_type',
            custom_props: {
                test_prop: 1
            }
        });
        expect(customBlock).toMatchSnapshot();
    });
});