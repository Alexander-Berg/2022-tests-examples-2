import * as React from 'react';
import { mount } from 'enzyme';
import { ReactElementsList } from 'typings/react';
import {
    jestSnapshotRenderTest,
    jestSnapshotShallowTest,
} from 'testing/jest-utils';
import { Tag } from '..';
import * as S from '../styles';
import { cleanup } from 'react-testing-library';

afterEach(cleanup);

const callback = jest.fn();

const shadowSnapshots: ReactElementsList = {
    'without disabled property provided': (
        <Tag onClick={callback} onRemove={callback}>
            Установка: от 19 до 25 мар 2018
        </Tag>
    ),
};

const renderSnapshots: ReactElementsList = {
    'with disabled property provided': (
        <Tag disabled={true} onClick={callback} onRemove={callback}>
            Установка: от 19 до 25 мар 2018
        </Tag>
    ),
};

describe('SegmentationSection', () => {
    describe('renders', () => {
        jestSnapshotShallowTest(shadowSnapshots);
        jestSnapshotRenderTest(renderSnapshots);
    });

    describe('Tag', () => {
        it('calls onClick callback', () => {
            const onClick = jest.fn();
            const component = mount(
                <Tag onClick={onClick} onRemove={callback}>
                    Установка: от 19 до 25 мар 2018
                </Tag>,
            );

            component.find(S.Label).simulate('click');

            expect(onClick).toHaveBeenCalledTimes(1);
        });

        it('calls onRemove callback', () => {
            const onRemove = jest.fn();
            const component = mount(
                <Tag onClick={callback} onRemove={onRemove}>
                    Установка: от 19 до 25 мар 2018
                </Tag>,
            );

            component.find(S.IconClose).simulate('click');

            expect(onRemove).toHaveBeenCalledTimes(1);
        });

        it('', () => {
            expect(true).toBe(true);
        });
    });
});
