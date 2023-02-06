import {render} from '@testing-library/react';
import omit from 'lodash/omit';
import moment from 'moment-timezone';

import {SchedulePreviewProps} from 'components/SchedulePreview';
import {useSchedulePreview} from 'components/SchedulePreview/queries/useSchedulePreview';

import {
    DATA_CY,
    prepareSchedulePreview,
    mockUseSchedulePreview,
} from './utils';

jest.mock('../../../components/SchedulePreview/queries/useSchedulePreview');
jest.mock('../../../utils/queries/schedules/useCheckDomainIsUnderAudit');

describe('Отображение превью графика / Отрисовка компонента', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    test('Отображается пустое превью с пустым массивом дат из ручки', () => {
        mockUseSchedulePreview.mockImplementation(() => {
            // при любой ошибке хука всегда возвращается пустой массив
            return [];
        });

        const props: SchedulePreviewProps = {
            offset: 0,
            startDate: moment(),
            scheduleType: 177,
        };

        const renderItem = prepareSchedulePreview(props);
        const {container, rerender} = render(renderItem);

        const result = container.querySelector(`[data-cy=${DATA_CY.EMPTY}]`);

        expect(result).toBeDefined();
        expect(result!.children).toHaveLength(0);
        expect(useSchedulePreview).toHaveBeenCalledWith({
            ...omit(props, ['scheduleType']),
            isWeeklyPattern: false,
            id: props.scheduleType,
        });

        const secondRenderItem = prepareSchedulePreview({
            ...props,
            scheduleType: 188,
        });

        rerender(secondRenderItem);

        expect(useSchedulePreview).toHaveBeenCalledWith({
            ...omit(props, ['scheduleType']),
            isWeeklyPattern: false,
            id: 188,
        });
        expect(useSchedulePreview).toHaveBeenCalledTimes(2);
    });
});
