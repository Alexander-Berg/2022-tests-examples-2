import {shallow} from 'enzyme';
import React from 'react';

import Col from '../Col';

describe('Col', () => {
    it('рендерит по дефолту', () => {
        const wrapper = shallow(<Col />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col');
    });
    it('рендерит со статическим размером', () => {
        const wrapper = shallow(<Col columns={3} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col_columns-xs_3');
    });
    it('рендерит с динамическим размером', () => {
        const wrapper = shallow(<Col columns={{xs: 2, sm: 4, xl: 2}} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col_columns-xs_2');
        expect(wrapper.prop('className')).toContain('amber-col_columns-sm_4');
        expect(wrapper.prop('className')).toContain('amber-col_columns-xl_2');
    });
    it('рендерит с кастомным компонентом', () => {
        const wrapper = shallow(<Col component="span" />);
        expect(wrapper.find('span').length).toBe(1);
    });
    test('с простым shrink', () => {
        const wrapper = shallow(<Col shrink={1} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col_shrink-xs_1');
    });
    test('с непростым shrink', () => {
        const wrapper = shallow(<Col shrink={{xs: 1, lg: 3}} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col_shrink-xs_1');
        expect(wrapper.prop('className')).toContain('amber-col_shrink-lg_3');
    });
    it('рендерит с простыми вертикальными паддингами', () => {
        const wrapper = shallow(<Col paddingTop="xs" paddingBottom="xs" />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col_paddingTop-xs_xs');
        expect(wrapper.prop('className')).toContain('amber-col_paddingBottom-xs_xs');
    });
    test('с непростыми вертикальными паддингами', () => {
        const wrapper = shallow(
            <Col paddingTop={{xs: 'm', xl: 'sm'}} paddingBottom={{xs: 'l', sm: 'm'}} />,
        );
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col_paddingTop-xs_m');
        expect(wrapper.prop('className')).toContain('amber-col_paddingTop-xl_sm');
        expect(wrapper.prop('className')).toContain('amber-col_paddingBottom-xs_l');
        expect(wrapper.prop('className')).toContain('amber-col_paddingBottom-sm_m');
    });
    test('с простым grow', () => {
        const wrapper = shallow(<Col grow={1} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col_grow-xs_1');
    });
    test('с непростым grow', () => {
        const wrapper = shallow(<Col grow={{xs: 1, lg: 3}} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col_grow-xs_1');
        expect(wrapper.prop('className')).toContain('amber-col_grow-lg_3');
    });
    test('с простым offset', () => {
        const wrapper = shallow(<Col offset={23} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col_offset-xs_23');
    });
    test('с непростым offset', () => {
        const wrapper = shallow(<Col offset={{xs: 1, lg: 3}} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col_offset-xs_1');
        expect(wrapper.prop('className')).toContain('amber-col_offset-lg_3');
    });
    test('с простым horizontalAlign', () => {
        const wrapper = shallow(<Col horizontalAlign="end" />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col_horizontalAlign-xs_end');
    });
    test('с непростым horizontalAlign', () => {
        const wrapper = shallow(<Col horizontalAlign={{xs: 'end', lg: 'beginning'}} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col_horizontalAlign-xs_end');
        expect(wrapper.prop('className')).toContain('amber-col_horizontalAlign-lg_beginning');
    });
    test('с простым verticalAlign', () => {
        const wrapper = shallow(<Col verticalAlign="top" />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col_verticalAlign-xs_top');
    });
    test('с непростым verticalAlign', () => {
        const wrapper = shallow(<Col verticalAlign={{xs: 'top', lg: 'bottom'}} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col_verticalAlign-xs_top');
        expect(wrapper.prop('className')).toContain('amber-col_verticalAlign-lg_bottom');
    });
    test('с простым flex', () => {
        const wrapper = shallow(<Col flex />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col_flex-xs');
    });
    test('с непростым flex', () => {
        const wrapper = shallow(<Col flex={{xs: true, lg: false}} />);
        expect(wrapper).toMatchSnapshot();
        expect(wrapper.prop('className')).toContain('amber-col_flex-xs');
        expect(wrapper.prop('className')).not.toContain('amber-col_flex-lg');
    });
});
