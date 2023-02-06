import { FixedSize, TextBlock, WrapContentSize } from '../../src';

describe('Text tests', (): void => {
    it('should create simple text block', (): void => {
        const textBlock = new TextBlock({
            text: 'bla',
            truncate: 'middle',
        });
        expect(textBlock).toMatchSnapshot();
    });

    it('should create text block with constrained dynamic width (for ios)', (): void => {
        const textBlock = new TextBlock({
            text: 'bla',
            width: new WrapContentSize({ constrained: 1 }),
        });

        expect(textBlock).toMatchSnapshot();
    });

    it('should create text with ellipsis', (): void => {
        const textBlock = new TextBlock({
            text: 'bla bla bla bla bla bla',
            width: new FixedSize({ value: 10 }),
            ellipsis: {
                text: '...',
                ranges: [
                    {
                        start: 2,
                        end: 3,
                    },
                ],
            },
        });
        expect(textBlock).toMatchSnapshot();
    });

    it('should create text with auto_ellipsis', (): void => {
        const textBlock = new TextBlock({
            text: 'bla bla bla bla bla',
            width: new FixedSize({ value: 10 }),
            auto_ellipsize: 1,
        });
        expect(textBlock).toMatchSnapshot();
    });
});
