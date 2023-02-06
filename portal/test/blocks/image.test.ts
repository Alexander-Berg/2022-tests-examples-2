import { FixedSize, IDivData, IDivExtension, ImageBlock, Template, TemplateCard, templateHelper, Templates, TextBlock } from '../../src';

describe('Image tests', (): void => {
    it('should create image with AspectRatio', (): void => {
        const imageBlock = new ImageBlock({
            width: new FixedSize({ value: 44 }),
            height: new FixedSize({ value: 44 }),
            image_url: 'https://i.imgur.com/qNJQKU8.png',
            aspect: { ratio: 0.75 },
        });

        expect(imageBlock).toMatchSnapshot();
    });

    it('should create image with AspectRatio from Template', (): void => {
        const imageBlock = {
            card: new ImageBlock({
                width: new FixedSize({ value: 44 }),
                height: new FixedSize({ value: 44 }),
                image_url: 'https://i.imgur.com/qNJQKU8.png',
                aspect: { ratio: new Template('aspectRatio') },
            }),
        };

        const helper = templateHelper(imageBlock);

        const divData: IDivData = {
            log_id: 'id',
            states: [
                {
                    state_id: 1,
                    div: helper.card({
                        aspectRatio: 1,
                    }),
                },
            ],
        };
        expect(new TemplateCard(new Templates(imageBlock), divData)).toMatchSnapshot();
    });

    it('should create image with preload', (): void => {
        const imageBlock = new ImageBlock({
            width: new FixedSize({ value: 44 }),
            height: new FixedSize({ value: 44 }),
            image_url: 'https://i.imgur.com/qNJQKU8.png',
            preload_required: 1,
        });

        expect(imageBlock).toMatchSnapshot();
    });

    it('should create image with preview', (): void => {
        const imageBlock = new ImageBlock({
            image_url: 'https://i.imgur.com/qNJQKU8.png',
            width: new FixedSize({ value: 44 }),
            height: new FixedSize({ value: 44 }),
            preview: 'test_preview',
            high_priority_preview_show: 1
        });

        expect(imageBlock).toMatchSnapshot();
    });

    it('should create image with tooltip', (): void => {
        const imageBlock = new ImageBlock({
            image_url: 'https://i.imgur.com/qNJQKU8.png',
            width: new FixedSize({ value: 44 }),
            height: new FixedSize({ value: 44 }),
            tooltips: [
                {
                    id: 'example_tooltip',
                    position: 'bottom-left',
                    div: new TextBlock({text: 'test'})
                }
            ]
        });

        expect(imageBlock).toMatchSnapshot();
    });

    it('should create image with extension', (): void => {
        const params: {[type: string]: string} = {
            'type': 'image'
        }
        const imageExtension: IDivExtension = {
            id: 'image_extension',
            params: params,
        }
        const imageBlock = new ImageBlock({
            image_url: 'https://i.imgur.com/qNJQKU8.png',
            width: new FixedSize({ value: 44 }),
            height: new FixedSize({ value: 44 }),
            extensions: [imageExtension],
        });

        expect(imageBlock).toMatchSnapshot();
    });
});
