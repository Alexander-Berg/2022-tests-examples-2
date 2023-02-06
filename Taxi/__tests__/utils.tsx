import {render} from '@testing-library/react';
import React from 'react';

import SchedulePreview, {SchedulePreviewProps} from 'components/SchedulePreview';
import {useSchedulePreview} from 'components/SchedulePreview/queries/useSchedulePreview';
import {useCheckDomainIsUnderAudit} from 'utils/queries/schedules/useCheckDomainIsUnderAudit';
import {createQueryProvider, createStoreProvider, flow} from 'utils/tests/renders';

export const DATA_CY = {
    WRAPPER: 'components_schedule-preview-wrapper',
    EMPTY: 'components_schedule-preview-empty',
};

export function prepareSchedulePreview(props: SchedulePreviewProps) {
    return flow(
        <SchedulePreview {...props}/>,
        [
            createStoreProvider,
            createQueryProvider,
        ],
    );
}

export const mockUseCheckDomainIsUnderAudit = useCheckDomainIsUnderAudit as jest.Mock<any>;
export const mockUseSchedulePreview = useSchedulePreview as jest.Mock<any>;

export function getMarkedPreviewItems(domChildren: HTMLCollection): boolean[] {
    const result: boolean[] = [];

    for (const item of domChildren) {
        const dataCYAttribute = item.getAttribute('data-cy');

        result.push(!!dataCYAttribute && dataCYAttribute.includes('active-true'));
    }

    return result;
}

export function renderBaseSchedule(props: SchedulePreviewProps) {
    const renderItem = prepareSchedulePreview(props);
    const {container, ...rest} = render(renderItem);

    const item = container.querySelector(`[data-cy=${DATA_CY.WRAPPER}]`);

    return {
        ...rest,
        container,
        item,
    };
}
