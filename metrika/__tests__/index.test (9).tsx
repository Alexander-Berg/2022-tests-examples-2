import * as React from 'react';
import { jestSnapshotRenderTest } from 'testing/jest-utils';
/**
 * при попытке сделать импорт из './BaseIcon' начинает возникать ошибка
 * Class extends value undefined is not a function or null
 * из-за циклических зависимостей
 */
import { BaseIcon, SvgDescription } from 'icons/BaseIcon';
import { shallow } from 'enzyme';

class MyIcon extends BaseIcon {
    block = 'MyIcon';

    getIconDescription(): SvgDescription {
        return {
            attributes: {
                viewBox: '0 0 10 10',
                width: '10',
                height: '10',
            },
            content: () => <line x1="0" y1="0" x2="10" y2="10" />,
        };
    }
}

describe('BaseIcon', () => {
    describe('supports incoming prop', () => {
        const incomingProps = {
            className: <MyIcon className="incomingClassName" />,
            'mix as object': (
                <MyIcon mix={{ block: 'button2', elem: 'icon' }} />
            ),
            'mix as array': (
                <MyIcon
                    mix={[
                        { block: 'button2', elem: 'icon' },
                        { block: 'another-block', elem: 'icon' },
                    ]}
                />
            ),
            mods: <MyIcon mods={{ mod1: 'val1', mod2: true }} />,
            'width, height, fill and stroke - will be passed to svg tag': (
                <MyIcon width="14px" height="14px" fill="black" stroke="red" />
            ),
        };

        jestSnapshotRenderTest(incomingProps);

        it('#onClick', () => {
            const onClick = jest.fn();
            const component = shallow(<MyIcon onClick={onClick} />);

            component.simulate('click');

            expect(onClick).toHaveBeenCalled();
        });
    });
});
