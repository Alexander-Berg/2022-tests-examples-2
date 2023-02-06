import moment from 'moment-timezone';

import {
    PA_FROM_RAW_TO_FORM_PERFECT_MOCK_FOR_UTC,
    PA_FROM_RAW_TO_FORM_PERFECT_MOCK_FOR_SAMARA,
} from 'api/projectActivities/__tests__/mocks';
import {convertProjectActivitiesFromRawToForm} from 'api/projectActivities/converters';

test('Project activities converts from raw to form correctly in UTC', () => {
    moment.locale('en');
    moment.tz.setDefault('UTC');
    const {payload: [projectActivities, projectActivitiesIdsToNames], result} = PA_FROM_RAW_TO_FORM_PERFECT_MOCK_FOR_UTC;

    expect(convertProjectActivitiesFromRawToForm(projectActivities, projectActivitiesIdsToNames)).toStrictEqual(result);
});

test('Project activities converts from raw to form correctly in Samara', () => {
    moment.locale('en');
    moment.tz.setDefault('Europe/Samara');
    const {payload: [projectActivities, projectActivitiesIdsToNames], result} = PA_FROM_RAW_TO_FORM_PERFECT_MOCK_FOR_SAMARA;

    expect(convertProjectActivitiesFromRawToForm(projectActivities, projectActivitiesIdsToNames)).toStrictEqual(result);
});
