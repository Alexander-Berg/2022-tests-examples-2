import * as React from 'react';
import { shallow } from 'enzyme';
import { ReactElementsList } from 'typings/react';
import {
    jestSnapshotRenderTest,
    jestSnapshotShallowTest,
} from 'testing/jest-utils';
import { CollapseToggler } from 'components/CollapseToggler';
import { Section } from '..';

const ComponentsForSnapshotRenderTest: ReactElementsList = {
    'with head string': (
        <Section>
            <Section.Header>test head</Section.Header>
        </Section>
    ),

    'with passed className prop': <Section className="className" />,

    'with head and body': (
        <Section>
            <Section.Header>test head</Section.Header>
            <Section.Body>test body</Section.Body>
        </Section>
    ),

    'with Header and passed className': (
        <Section>
            <Section.Header className="className">test head</Section.Header>
        </Section>
    ),

    'with Body and passed className': (
        <Section>
            <Section.Body className="className">test head</Section.Body>
        </Section>
    ),

    collapsable: (
        <Section collapsable={true}>
            <Section.Header>
                <div>Hello world</div>
            </Section.Header>
        </Section>
    ),

    collapsed: (
        <Section collapsable={true} collapsed={true}>
            <Section.Header>
                <div>Hello world</div>
            </Section.Header>
        </Section>
    ),
};

// why use `shallow().dive()` instead of `render()`?
// with collapseType="tumbler" props we use Tumbler component from lego
// so after changes in lego this snapshot might become broken using `render`
const ComponentsForSnapshotShallowTest: ReactElementsList = {
    'collapsable tumbler': (
        <Section collapsable={true} collapseType="tumbler">
            <Section.Header>
                <div>Hello world</div>
            </Section.Header>
        </Section>
    ),
};

describe('Section', () => {
    describe('renders', () => {
        jestSnapshotRenderTest(ComponentsForSnapshotRenderTest);
        jestSnapshotShallowTest(ComponentsForSnapshotShallowTest);
    });

    describe('#onChange', () => {
        it('not called on uncollapsable Section', () => {
            const onChange = jest.fn();
            const component = shallow(
                <Section onChange={onChange}>
                    <Section.Header>
                        <div>Hello world</div>
                    </Section.Header>
                </Section>,
            );

            component.find(Section.Controls).simulate('click');

            expect(onChange).toHaveBeenCalledTimes(0);
        });

        it('opened Section on initial render', () => {
            const onChange = jest.fn();
            const component = shallow(
                <Section collapsable={true} onChange={onChange}>
                    <Section.Header>
                        <div>Hello world</div>
                    </Section.Header>
                </Section>,
            );

            component.find(CollapseToggler).simulate('click');
            expect(onChange).toHaveBeenCalledWith(true);

            component.find(CollapseToggler).simulate('click');
            expect(onChange).toHaveBeenLastCalledWith(false);
        });

        it('collapsed Section on initial render', () => {
            const onChange = jest.fn();
            const component = shallow(
                <Section
                    collapsable={true}
                    collapsed={true}
                    onChange={onChange}
                >
                    <Section.Header>
                        <div>Hello world</div>
                    </Section.Header>
                </Section>,
            );

            component.find(CollapseToggler).simulate('click');
            expect(onChange).toHaveBeenCalledWith(false);

            component.find(CollapseToggler).simulate('click');
            expect(onChange).toHaveBeenLastCalledWith(true);
        });
    });
});
