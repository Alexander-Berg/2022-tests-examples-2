/* eslint-disable jest/no-standalone-expect */

import * as React from 'react';

import { mount, render, configure } from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

import { Humanize } from '..';

configure({ adapter: new Adapter() });
/* yaspeller ignore:start */
function jestSnapshotRenderTest(components: any): void {
    Object.entries(components).forEach(([title, component]) => {
        // eslint-disable-next-line jest/valid-title
        it(title, () => {
            const tree = render(component as any);
            expect(tree).toMatchSnapshot();
        });
    });
}

const customFormatters = {
    millionsOfDollars: (val: string) => {
        return val + ' millions of dollars!';
    },
    reverse: (val: string) => {
        return String(val).split('').reverse().join('');
    },
};
type CustomFormatters = keyof typeof customFormatters;

const overrideDefaultFormatters = {
    number: (val: string) => {
        return `this is overrided number: ${val}`;
    },
};
type OverrideFormatters = keyof typeof overrideDefaultFormatters;

// It's important to wrap result in span,
// otherwise it's rendered in snapshot as null
const ComponentsForSnapshotRenderTest = {
    'default number': (
        <Humanize value={99} type="number">
            {(v) => <span>{v}</span>}
        </Humanize>
    ),
    'default percentage': (
        <Humanize value={99} type="percentage">
            {(v) => <span>{v}</span>}
        </Humanize>
    ),
    'default float': (
        <Humanize value={99} type="float">
            {(v) => <span>{v}</span>}
        </Humanize>
    ),
    'custom millionsOfDollars': (
        <Humanize<CustomFormatters>
            value={100000}
            type="millionsOfDollars"
            formatters={customFormatters}
        >
            {(v) => <span>{v}</span>}
        </Humanize>
    ),
    'custom reverse': (
        <Humanize<CustomFormatters>
            value={"Hello I'm reversed string!"}
            type="reverse"
            formatters={customFormatters}
        >
            {(v) => <span>{v}</span>}
        </Humanize>
    ),
    'overrode default number': (
        <Humanize<OverrideFormatters>
            value="99"
            type="number"
            formatters={overrideDefaultFormatters}
        >
            {(v) => <span>{v}</span>}
        </Humanize>
    ),
    'default formatter, but pass custom formatters': (
        <Humanize<OverrideFormatters>
            value="99"
            type="percentage"
            formatters={overrideDefaultFormatters}
        >
            {(v) => <span>{v}</span>}
        </Humanize>
    ),
    'without children': <Humanize value="99" type="percentage" />,
    'default currency': (
        <Humanize value="99" type="currency">
            {(v) => <span>{v}</span>}
        </Humanize>
    ),
    'default big currency': (
        <Humanize value="9999.9" type="currency">
            {(v) => <span>{v}</span>}
        </Humanize>
    ),
    'default currency with symbol': (
        <Humanize value="99" type="currency" currency="RUB">
            {(v) => <span>{v}</span>}
        </Humanize>
    ),
};

describe('Humanize', () => {
    describe('renders', () => {
        jestSnapshotRenderTest(ComponentsForSnapshotRenderTest);
    });
    describe('number casts correctly', () => {
        let component;

        component = mount(<Humanize value={0.1} type="number" />);
        expect(component.text()).toEqual('0');

        component = mount(<Humanize value={0} type="number" />);
        expect(component.text()).toEqual('0');

        component = mount(<Humanize value={10} type="number" />);
        expect(component.text()).toEqual('10');

        component = mount(<Humanize value={100.1} type="number" />);
        expect(component.text()).toEqual('100');

        component = mount(<Humanize value={10000} type="number" />);
        expect(component.text()).toEqual('10 000');

        component = mount(<Humanize value={1001010.023} type="number" />);
        expect(component.text()).toEqual('1 001 010');

        describe('with compress', () => {
            component = mount(<Humanize compress value={2800} type="number" />);
            expect(component.text()).toEqual('2,8 тыс.');

            component = mount(
                <Humanize compress value={280000} type="number" />,
            );
            expect(component.text()).toEqual('280 тыс.');

            component = mount(
                <Humanize compress value={2.8 * 10 ** 6} type="number" />,
            );
            expect(component.text()).toEqual('2,8 млн');

            component = mount(
                <Humanize compress value={2.8 * 10 ** 9} type="number" />,
            );
            expect(component.text()).toEqual('2,8 млрд');

            component = mount(
                <Humanize compress value={2.8 * 10 ** 12} type="number" />,
            );
            expect(component.text()).toEqual('2,8 трл.');

            component = mount(
                <Humanize compress value={2.8 * 10 ** 15} type="number" />,
            );
            expect(component.text()).toEqual('2,8 кв.');

            component = mount(
                <Humanize compress value={2.8 * 10 ** 18} type="number" />,
            );
            expect(component.text()).toEqual('2,8 квин.');

            component = mount(
                <Humanize compress value={2.8 * 10 ** 21} type="number" />,
            );
            expect(component.text()).toEqual('2,8 секст.');

            component = mount(
                <Humanize compress value={2.8 * 10 ** 24} type="number" />,
            );
            expect(component.text()).toEqual('2,8 септ.');

            component = mount(
                <Humanize compress value={2.8 * 10 ** 27} type="number" />,
            );
            expect(component.text()).toEqual('2,8 окт.');

            component = mount(
                <Humanize compress value={2.8 * 10 ** 30} type="number" />,
            );
            expect(component.text()).toEqual('2,8 нон.');

            component = mount(
                <Humanize compress value={2.8 * 10 ** 33} type="number" />,
            );
            expect(component.text()).toEqual('2,8 дец.');
        });

        describe('with threshold', () => {
            component = mount(
                <Humanize
                    value={312345}
                    type="number"
                    approximationThreshold={3}
                />,
            );
            expect(component.text()).toEqual('312 000');

            component = mount(
                <Humanize
                    value={312345}
                    type="number"
                    approximationThreshold={0.3}
                />,
            );
            expect(component.text()).toEqual('312 345');
        });
    });
    describe('float casts correctly', () => {
        let component;

        component = mount(<Humanize value={0} type="float" />);
        expect(component.text()).toEqual('0');

        component = mount(<Humanize value={0.1} type="float" />);
        expect(component.text()).toEqual('0,1');

        component = mount(<Humanize value={0.01} type="float" />);
        expect(component.text()).toEqual('0,01');

        component = mount(<Humanize value={0.001} type="float" />);
        expect(component.text()).toEqual('10-3');

        component = mount(<Humanize value={0.002} type="float" />);
        expect(component.text()).toEqual('2×10-3');

        component = mount(<Humanize value={0.0089} type="float" />);
        expect(component.text()).toEqual('8,9×10-3');

        describe('tricky cases', () => {
            component = mount(<Humanize value={0.055} type="float" />);
            expect(component.text()).toEqual('0,06');

            component = mount(<Humanize value={0.555} type="float" />);
            expect(component.text()).toEqual('0,56');

            component = mount(<Humanize value={0.145} type="float" />);
            expect(component.text()).toEqual('0,15');

            component = mount(<Humanize value={1.005} type="float" />);
            expect(component.text()).toEqual('1,01');

            component = mount(
                <Humanize value={0.0555} type="float" accuracy={3} />,
            );
            expect(component.text()).toEqual('0,056');

            component = mount(
                <Humanize value={0.0145} type="float" accuracy={3} />,
            );
            expect(component.text()).toEqual('0,015');

            component = mount(
                <Humanize value={1.0005} type="float" accuracy={3} />,
            );
            expect(component.text()).toEqual('1,001');
        });

        describe('with accuracy', () => {
            component = mount(<Humanize value={0} type="float" accuracy={3} />);
            expect(component.text()).toEqual('0');

            component = mount(
                <Humanize value={0.1} type="float" accuracy={3} />,
            );
            expect(component.text()).toEqual('0,1');

            component = mount(
                <Humanize value={0.01} type="float" accuracy={3} />,
            );
            expect(component.text()).toEqual('0,01');

            component = mount(
                <Humanize value={0.001} type="float" accuracy={3} />,
            );
            expect(component.text()).toEqual('10-3');

            component = mount(
                <Humanize value={0.002} type="float" accuracy={3} />,
            );
            expect(component.text()).toEqual('2×10-3');

            component = mount(
                <Humanize value={0.0089} type="float" accuracy={3} />,
            );
            expect(component.text()).toEqual('8,9×10-3');
        });

        describe('with threshold', () => {
            component = mount(
                <Humanize
                    value={0}
                    type="float"
                    approximationThreshold={0.001}
                />,
            );
            expect(component.text()).toEqual('0');

            component = mount(
                <Humanize
                    value={0.1}
                    type="float"
                    approximationThreshold={0.001}
                />,
            );
            expect(component.text()).toEqual('0,1');

            component = mount(
                <Humanize
                    value={0.01}
                    type="float"
                    approximationThreshold={0.001}
                />,
            );
            expect(component.text()).toEqual('0,01');

            component = mount(
                <Humanize
                    value={0.001}
                    type="float"
                    approximationThreshold={0.001}
                />,
            );
            expect(component.text()).toEqual('10-3');

            component = mount(
                <Humanize
                    value={0.002}
                    type="float"
                    approximationThreshold={0.001}
                />,
            );
            expect(component.text()).toEqual('2×10-3');

            component = mount(
                <Humanize
                    value={0.0089}
                    type="float"
                    approximationThreshold={0.001}
                />,
            );
            expect(component.text()).toEqual('8,9×10-3');

            component = mount(
                <Humanize
                    value={0.0001}
                    type="float"
                    approximationThreshold={0.001}
                />,
            );
            expect(component.text()).toEqual('< 0,001');
        });
    });
    describe('percentage casts correctly', () => {
        let component;

        component = mount(<Humanize value={0} type="percentage" />);
        expect(component.text()).toEqual('0 %');

        component = mount(<Humanize value={0.1} type="percentage" />);
        expect(component.text()).toEqual('0,1 %');

        component = mount(<Humanize value={0.01} type="percentage" />);
        expect(component.text()).toEqual('0,01 %');

        component = mount(<Humanize value={0.001} type="percentage" />);
        expect(component.text()).toEqual('10-3 %');

        component = mount(<Humanize value={0.002} type="percentage" />);
        expect(component.text()).toEqual('2×10-3 %');

        component = mount(<Humanize value={0.0089} type="percentage" />);
        expect(component.text()).toEqual('8,9×10-3 %');

        component = mount(<Humanize value={99.98341} type="percentage" />);
        expect(component.text()).toEqual('99,98 %');

        describe('with accuracy', () => {
            component = mount(
                <Humanize value={0} type="percentage" accuracy={3} />,
            );
            expect(component.text()).toEqual('0 %');

            component = mount(
                <Humanize value={0.1} type="percentage" accuracy={3} />,
            );
            expect(component.text()).toEqual('0,1 %');

            component = mount(
                <Humanize value={0.01} type="percentage" accuracy={3} />,
            );
            expect(component.text()).toEqual('0,01 %');

            component = mount(
                <Humanize value={0.001} type="percentage" accuracy={3} />,
            );
            expect(component.text()).toEqual('10-3 %');

            component = mount(
                <Humanize value={0.002} type="percentage" accuracy={3} />,
            );
            expect(component.text()).toEqual('2×10-3 %');

            component = mount(
                <Humanize value={0.0089} type="percentage" accuracy={3} />,
            );
            expect(component.text()).toEqual('8,9×10-3 %');
        });

        describe('with threshold', () => {
            component = mount(
                <Humanize
                    value={0}
                    type="percentage"
                    approximationThreshold={0.01}
                />,
            );
            expect(component.text()).toEqual('0 %');

            component = mount(
                <Humanize
                    value={0.1}
                    type="percentage"
                    approximationThreshold={0.01}
                />,
            );
            expect(component.text()).toEqual('0,1 %');

            component = mount(
                <Humanize
                    value={0.01}
                    type="percentage"
                    approximationThreshold={0.01}
                />,
            );
            expect(component.text()).toEqual('0,01 %');

            component = mount(
                <Humanize
                    value={0.001}
                    type="percentage"
                    approximationThreshold={0.01}
                />,
            );
            expect(component.text()).toEqual('< 0,01 %');
        });
    });
    describe('currency casts correctly', () => {
        let component;

        component = mount(<Humanize value={0} type="currency" />);
        expect(component.text()).toEqual('0,00');

        component = mount(<Humanize value={0.1} type="currency" />);
        expect(component.text()).toEqual('0,10');

        component = mount(<Humanize value={0.01} type="currency" />);
        expect(component.text()).toEqual('0,01');

        component = mount(<Humanize value={0.001} type="currency" />);
        expect(component.text()).toEqual('10-3');

        component = mount(<Humanize value={0.002} type="currency" />);
        expect(component.text()).toEqual('2×10-3');

        component = mount(<Humanize value={0.0089} type="currency" />);
        expect(component.text()).toEqual('8,9×10-3');

        component = mount(<Humanize value={1000} type="currency" />);
        expect(component.text()).toEqual('1 000,00');

        component = mount(<Humanize value={10000.1} type="currency" />);
        expect(component.text()).toEqual('10 000,10');

        describe('tricky cases', () => {
            component = mount(<Humanize value={0.055} type="currency" />);
            expect(component.text()).toEqual('0,06');

            component = mount(<Humanize value={0.555} type="currency" />);
            expect(component.text()).toEqual('0,56');

            component = mount(<Humanize value={0.145} type="currency" />);
            expect(component.text()).toEqual('0,15');

            component = mount(<Humanize value={1.005} type="currency" />);
            expect(component.text()).toEqual('1,01');

            component = mount(<Humanize value={0.0555} type="currency" />);
            expect(component.text()).toEqual('0,06');

            component = mount(<Humanize value={0.0145} type="currency" />);
            expect(component.text()).toEqual('0,01');

            component = mount(<Humanize value={1.0005} type="currency" />);
            expect(component.text()).toEqual('1,00');
        });

        describe('with symbols', () => {
            component = mount(
                <Humanize value={0} type="currency" currency="RUB" />,
            );
            expect(component.text()).toEqual('0,00 ₽');

            component = mount(
                <Humanize value={0.1} type="currency" currency="USD" />,
            );
            expect(component.text()).toEqual('$ 0,10');

            component = mount(
                <Humanize value={0.01} type="currency" currency="RUB" />,
            );
            expect(component.text()).toEqual('0,01 ₽');

            component = mount(
                <Humanize value={0.001} type="currency" currency="USD" />,
            );
            expect(component.text()).toEqual('$ 10-3');

            component = mount(
                <Humanize value={0.002} type="currency" currency="USD" />,
            );
            expect(component.text()).toEqual('$ 2×10-3');

            component = mount(
                <Humanize value={0.0089} type="currency" currency="USD" />,
            );
            expect(component.text()).toEqual('$ 8,9×10-3');
        });

        describe('with unexisted currency', () => {
            component = mount(
                <Humanize value={0} type="currency" currency="YNDX" />,
            );
            expect(component.text()).toEqual('0,00 YNDX');

            component = mount(
                <Humanize value={0.1} type="currency" currency="YNDX" />,
            );
            expect(component.text()).toEqual('0,10 YNDX');
        });
    });
});
/* yaspeller ignore:end */
