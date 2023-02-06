import {
    AnimationSet,
    DivStateBlock,
    IDivData,
    Template,
    TemplateCard,
    templateHelper,
    Templates,
    TextBlock
} from '../../src';

describe('Animation tests', (): void => {

    it('should create simple animation', (): void => {
        const block = new DivStateBlock({
            div_id: 'card_subscribe',
            states: [
                {
                    state_id: 'initial',
                    div: new TextBlock({
                        text: 'Test',
                    }),
                    animation_in: new AnimationSet({
                        items: [
                            {
                                name: 'fade',
                                duration: 500,
                            },
                            {
                                name: 'scale',
                                duration: 500,
                                start_value: 0.5,
                                end_value: 1,
                            },
                        ],
                    }),
                    animation_out: new AnimationSet({
                        items: [
                            {
                                name: 'fade',
                                duration: 500,
                            },
                            {
                                name: 'scale',
                                duration: 500,
                                start_value: 1,
                                end_value: 0.5,
                            },
                        ],
                    }),
                },
            ],
        });
        
        expect(block).toMatchSnapshot();
    });

    it('should create animation with templates', (): void => {
        const tMap = {
            card: new TextBlock({
                text: new Template('name'),
                action_animation: {
                    name: 'set',
                    items: [
                        {
                            name: 'fade',
                            start_value: new Template('animation_start_value'),
                            end_value: 1
                        }
                    ]
                }
            })
        };

        const divData: IDivData = {
            log_id: 'id',
            states: [
                {
                    state_id: 1,
                    div: templateHelper(tMap).card({
                        name: 'some name',
                        animation_start_value: 0
                    })
                }
            ]
        };
        
        expect(new TemplateCard(new Templates(tMap), divData)).toMatchSnapshot();
    });

});
