import {
    templateHelper,
    IDivData,
    Template, TemplateCard,
    Templates,
    PagerBlock, TextBlock,
    PageSize, PercentageSize, FixedSize, NeighbourPageSize
} from '../../src';

import {cloneObject} from '../../src/helper';

describe('Div pager test', (): void => {
    it('should create simple pager block', (): void => {
        const block = new PagerBlock({
            items: [
                new TextBlock({
                    text: 'bla'
                })
            ],
            layout_mode: new PageSize({page_width: new PercentageSize({value: 1})})
        });

        expect(cloneObject(block)).toMatchSnapshot();
    });

    it('should create block with all properties', (): void => {
        const block = new PagerBlock({
            items: [
                new TextBlock({
                    text: 'bla'
                })
            ],
            layout_mode: new NeighbourPageSize({neighbour_page_width: new FixedSize({value: 1})}),
            item_spacing: new FixedSize({value: 1}),
            orientation: 'horizontal',
            restrict_parent_scroll: 1
        });

        expect(cloneObject(block)).toMatchSnapshot();
    });

    it('should create templated indicator block', (): void => {
        const templates = new Templates([
            {
                type: 'title_text',
                block: new PagerBlock({
                    items: [
                        new TextBlock({
                            text: new Template('txt')
                        })
                    ],
                    layout_mode: new Template('mode'),
                    item_spacing: new Template('spacing'),
                    orientation:  new Template('display'),
                    restrict_parent_scroll:  new Template('scroll'),
                })
            }
        ]);

        expect(templates.blocks).toMatchSnapshot();
    });

    it('should create card with templated properties in indicator block', (): void => {
        const tMap = {
            card:new PagerBlock({
                items: [
                    new TextBlock({
                        text: new Template('txt')
                    })
                ],
                layout_mode: new Template('mode'),
                item_spacing: new Template('spacing'),
                orientation:  new Template('display'),
                restrict_parent_scroll:  new Template('scroll'),
            })
        }

        const helper = templateHelper(tMap);

        const divData: IDivData = {
            log_id: 'id',
            states: [
                {
                    state_id: 1,
                    div: helper.card({
                        txt: 'bla',
                        mode: new NeighbourPageSize({neighbour_page_width: new FixedSize({value: 1})}),
                        spacing: new FixedSize({value: 1}),
                        display: 'vertical',
                        scroll: 0
                    })
                }
            ]
        };

        expect(new TemplateCard(new Templates(tMap), divData)).toMatchSnapshot();
    });
});