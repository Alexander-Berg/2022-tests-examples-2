import {shallow} from 'enzyme';
import React from 'react';

import Row from '../Row';

describe('Row', () => {
    it('рендерит по дефолту', () => {
        const wrapper = shallow(<Row />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-row');
    });

    it('рендерит с кастомным компонентом', () => {
        const wrapper = shallow(<Row component="span" />);
        expect(wrapper.find('span').length).toBe(1);
    });

    test('рендерит с простыми verticalPadding', () => {
        const wrapper = shallow(<Row paddingTop="xs" paddingBottom="xs" />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-row_paddingTop-xs_xs');
        expect(wrapper.prop('className')).toContain('amber-row_paddingBottom-xs_xs');
    });

    test('с непростыми verticalPadding', () => {
        const wrapper = shallow(
            <Row paddingTop={{xs: 'm', xl: 'sm'}} paddingBottom={{xs: 'l', sm: 'm'}} />,
        );
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-row_paddingTop-xs_m');
        expect(wrapper.prop('className')).toContain('amber-row_paddingTop-xl_sm');
        expect(wrapper.prop('className')).toContain('amber-row_paddingBottom-xs_l');
        expect(wrapper.prop('className')).toContain('amber-row_paddingBottom-sm_m');
    });

    test('рендерит с простыми horizontalPadding', () => {
        const wrapper = shallow(<Row paddingLeft="xs" paddingRight="xs" />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-row_paddingLeft-xs_xs');
        expect(wrapper.prop('className')).toContain('amber-row_paddingRight-xs_xs');
    });
    test('с непростыми horizontalPadding', () => {
        const wrapper = shallow(
            <Row paddingLeft={{xs: 'm', xl: 'sm'}} paddingRight={{xs: 'l', sm: 'm'}} />,
        );
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-row_paddingLeft-xs_m');
        expect(wrapper.prop('className')).toContain('amber-row_paddingLeft-xl_sm');
        expect(wrapper.prop('className')).toContain('amber-row_paddingRight-xs_l');
        expect(wrapper.prop('className')).toContain('amber-row_paddingRight-sm_m');
    });
    test('с простым grow', () => {
        const wrapper = shallow(<Row grow={1} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-row_grow-xs_1');
    });
    test('с непростым grow', () => {
        const wrapper = shallow(<Row grow={{xs: 1, lg: 3}} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-row_grow-xs_1');
        expect(wrapper.prop('className')).toContain('amber-row_grow-lg_3');
    });
    test('с простым shrink', () => {
        const wrapper = shallow(<Row shrink={1} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-row_shrink-xs_1');
    });
    test('с непростым shrink', () => {
        const wrapper = shallow(<Row shrink={{xs: 1, lg: 3}} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-row_shrink-xs_1');
        expect(wrapper.prop('className')).toContain('amber-row_shrink-lg_3');
    });
    test('с простым horizontalAlign', () => {
        const wrapper = shallow(<Row horizontalAlign="end" />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-row_horizontalAlign-xs_end');
    });
    test('с непростым horizontalAlign', () => {
        const wrapper = shallow(<Row horizontalAlign={{xs: 'end', lg: 'beginning'}} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-row_horizontalAlign-xs_end');
        expect(wrapper.prop('className')).toContain('amber-row_horizontalAlign-lg_beginning');
    });
    test('с простым verticalAlign', () => {
        const wrapper = shallow(<Row verticalAlign="top" />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-row_verticalAlign-xs_top');
    });
    test('с непростым verticalAlign', () => {
        const wrapper = shallow(<Row verticalAlign={{xs: 'top', lg: 'bottom'}} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-row_verticalAlign-xs_top');
        expect(wrapper.prop('className')).toContain('amber-row_verticalAlign-lg_bottom');
    });
    test('с простым reverse', () => {
        const wrapper = shallow(<Row reverse />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-row_reverse-xs');
    });
    test('с непростым reverse', () => {
        const wrapper = shallow(<Row reverse={{xs: true, lg: false}} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-row_reverse-xs');
        expect(wrapper.prop('className')).not.toContain('amber-row_reverse-lg');
    });
});
