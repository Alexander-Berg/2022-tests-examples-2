import {
    templateHelper,
    IDivData,
    Template, TemplateCard,
    Templates, FixedSize,
    IndicatorBlock,
    RoundedRectangleShape,
    rewriteVars
} from '../../src';

import {cloneObject} from '../../src/helper';

describe('Div indicator test', (): void => {
    it('should create simple indicator block', (): void => {
        const block = new IndicatorBlock({
            pager_id: 'bla'
        });

        expect(cloneObject(block)).toMatchSnapshot();
    });

    it('should create block with all properties', (): void => {
        const block = new IndicatorBlock({
            pager_id: 'bla',
            space_between_centers: new FixedSize({value: 1}),
            inactive_item_color: '#000',
            active_item_color: '#000',
            shape: new RoundedRectangleShape({
                item_height: new FixedSize({value: 1, unit: 'sp'}),
                item_width: new FixedSize({value: 1}),
                corner_radius: new FixedSize({value: 1, unit: 'dp'}),
            }),
            active_item_size: 1,
            minimum_item_size: 1,
            animation: 'worm'
        });

        expect(cloneObject(block)).toMatchSnapshot();
    });


    it('should create templated indicator block', (): void => {
        const templates = new Templates([
            {
                type: 'title_text',
                block: new IndicatorBlock({
                    pager_id: new Template('id'),
                    space_between_centers: new Template('space'),
                    inactive_item_color: new Template('color1'),
                    active_item_color: new Template('color2'),
                    shape: new RoundedRectangleShape({
                        item_height: new Template('item_height')
                    }),
                    active_item_size: new Template('a_size'),
                    minimum_item_size: new Template('m_size'),
                    animation: new Template('anima'),
                })
            }
        ]);


        expect(templates.blocks).toMatchSnapshot();
    });

    it('should create card with templated properties in indicator block', (): void => {
        let tMap = {
            card: new IndicatorBlock({
                pager_id: new Template('id'),
                space_between_centers: new Template('space'),
                inactive_item_color: new Template('color1'),
                active_item_color: new Template('color2'),
                shape: new RoundedRectangleShape({
                    item_height: new Template('s_height')
                }),
                active_item_size: new Template('a_size'),
                minimum_item_size: new Template('m_size'),
                animation: new Template('anima'),
            })
        };
        tMap = rewriteVars(tMap);

        const helper = templateHelper(tMap);

        const divData: IDivData = {
            log_id: 'id',
            states: [
                {
                    state_id: 1,
                    div: helper.card({
                        id: 'red',
                        space: new FixedSize({value: 1}),
                        color1: '#000',
                        color2: '#000',
                        s_height: new FixedSize({value:1}),
                        a_size: 1,
                        m_size: 1,
                        anima: 'slider',
                    })
                }
            ]
        };

        expect(new TemplateCard(new Templates(tMap), divData)).toMatchSnapshot();
    });
});
