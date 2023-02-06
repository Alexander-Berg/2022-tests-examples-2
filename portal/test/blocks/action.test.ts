import {
    templateHelper,
    IDivData,
    Template, TemplateCard,
    Templates,
    TextBlock
} from '../../src';

import {cloneObject} from '../../src/helper';

describe('Div action test', (): void => {
    it('should create text block with action', (): void => {
        const textBlock = new TextBlock({
            text: 'bla',
            action: {
                log_id: 'id',
                url: 'ya.ru'
            }
        });

        expect(cloneObject(textBlock)).toMatchSnapshot();
    });

    it('should create block with payload action', (): void => {
        const textBlock = new TextBlock({
            text: 'bla',
            action: {
                log_id: 'id',
                url: 'ya.ru',
                payload: {
                    a: 1,
                    b: 2
                }
            }
        });

        expect(cloneObject(textBlock)).toMatchSnapshot();
    });

    it('should create block with action with hover type background-color', (): void => {
        const textBlock = new TextBlock({
            text: 'bla',
            action: {
                log_id: 'id',
                url: 'ya.ru',
                hover: {
                    type: 'background-color',
                    color: 'red'
                }
            }
        });

        expect(cloneObject(textBlock)).toMatchSnapshot();
    });

    /*it('should create block with action with hover type translate', (): void => {
        const textBlock = new TextBlock({
            text: 'bla',
            action: {
                log_id: 'id',
                url: 'ya.ru',
                hover: {
                    type: 'translate'
                }
            }
        });

        expect(cloneObject(textBlock)).toMatchSnapshot();
    });*/

    it('should create template with action nested properties', (): void => {
        const templates = new Templates([
            {
                type: 'title_text',
                block: new TextBlock({
                    text: 'bla',
                    action: {
                        log_id: 'id',
                        url: 'ya.ru',
                        hover: {
                            type: 'background-color',
                            color: new Template('bgHoverColor')
                        }
                    }
                })
            }
        ]);

        expect(templates.blocks).toMatchSnapshot();
    });

    it('should create card with templated action properties', (): void => {
        const tMap = {
            card: new TextBlock({
                text: 'bla',
                action: {
                    log_id: 'id',
                    url: new Template('actionUrl'),
                    hover: {
                        type: 'background-color',
                        color: new Template('bgHoverColor')
                    }
                }
            })
        }

        const helper = templateHelper(tMap);

        const divData: IDivData = {
            log_id: 'id',
            states: [
                {
                    state_id: 1,
                    div: helper.card({
                        bgHoverColor: 'red',
                        actionUrl: 'ya.ru'
                    })
                }
            ]
        };

        expect(new TemplateCard(new Templates(tMap), divData)).toMatchSnapshot();
    });
});
