import {assert} from 'chai'

import {
    TitleBlock, ContainerBlock, UniversalBlock,
    NumericSize, PredefinedSize, SolidBackground, NonEmptyArray
} from '../../src';

import {
    SimpleContainer,
    ContainerInContainer,
    ContainerWithUniversal,
    ContainerWithAllProperties
} from '../mocks/index';

describe('Div container test', () => {
    let title: TitleBlock, simpleContainer: ContainerBlock;

    before(() => {
        title = new TitleBlock({
            text: "text",
            text_style: 'title_s'
        });

        simpleContainer = new ContainerBlock({
            children: [title],
            width: new NumericSize({value: 100, unit: "dp"}),
            height: new PredefinedSize({value: "match_parent"})
        })

    });

    it('should create simple container', () => {

        assert.deepEqual(simpleContainer.div(), SimpleContainer);
    });

    it('should create container inside other container', () => {

        let container: ContainerBlock = new ContainerBlock({
            alignment_vertical: "top",
            children: [simpleContainer],
            width: new NumericSize({value: 100, unit: "sp"}),
            height: new PredefinedSize({value: "wrap_content"})
        });

        container.alignment_horizontal = "center";
        container.children.unshift(title);
        container.children.push(title);

        assert.deepEqual(container.div(), ContainerInContainer);
    });

    it('should create container with universal block', () => {

        let universal: UniversalBlock = new UniversalBlock({
                text: 'text',
                title: 'title',
                text_max_lines: 1,
                title_max_lines: 1,
                text_style: "text_s",
                title_style: "text_m_medium"
            }
        );
        let container: ContainerBlock = new ContainerBlock({
            alignment_horizontal: "right",
            alignment_vertical: "bottom",
            children: [universal],
            width: new NumericSize({value: 100, unit: 'sp'}),
            height: new PredefinedSize({value: "match_viewport"})
        });

        assert.deepEqual(container.div(), ContainerWithUniversal);
    });

    it('should create container with all properties', () => {
        let container: ContainerBlock = new ContainerBlock({
            alignment_horizontal: "right",
            alignment_vertical: "center",
            children: [title],
            width: new NumericSize({value: 100}),
            height: new NumericSize({value: 100}),
            action: {
                url: 'ya.ru',
                log_id: 'id'
            },
            padding_modifier: {
                size: "match_parent",
                position: "left"
            },
            frame: {
                color: "#000",
                style: "shadow"
            },
            background: [
                new SolidBackground({color:"#000"})
            ]
        });

        assert.deepEqual(container.div(), ContainerWithAllProperties);
    });
});