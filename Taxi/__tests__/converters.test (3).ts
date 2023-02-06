import moment from 'moment-timezone';

import {
    getMinutesDurationFromMoment,
    filtersFromClientToServer,
    prepareChartFiltersToRequest,
    prepareDisciplineFiltersToRequest,
    convertBreaks,
    prepareOperatorsShift,
    updateOperatorsShiftWithForm,
    convertWorkBreakToServer,
    convertProjectActivityToServer,
    prepareShiftForSaveRequest,
    convertTableShiftToServerShift,
    convertPeriodForRequest,
    normalizeShiftsPayload,
} from '../converters';
import {ShiftConfirmationMode} from '../types';

import {
    FILTERS_CLIENT_TO_SERVER_MOCK,
    PREPARE_CHART_FILTERS_MOCK,
    PREPARE_DISCIPLINE_FILTERS_MOCK,
    CONVERT_BREAKS_MOCK,
    PREPARE_OPERATORS_SHIFT_MOCK,
    EDIT_SHIFT_FORM_MOCK,
    CONVERT_PA_TO_SERVER_MOCK,
    PREPARE_SHIFT_FOR_SAVE_MOCK,
    CONVERT_TABLE_SHIFT_TO_SERVER_MOCK,
    CONVERT_PERIOD_FOR_REQUEST_MOCK,
    NORMALIZE_SHIFTS_PAYLOAD_MOCK,
} from './mocks';

test('getMinutesDurationFromMoment calculate diff correctly', () => {
    const from = moment('2021-08-25T00:00:00+03:00');
    const to = moment('2021-08-25T02:00:00+03:00');

    expect(getMinutesDurationFromMoment([from, to])).toEqual(120);
});

// кейс с выбором конца «конец смены» тоже проверяется тут
test('filtersFromClientToServer converts correctly', () => {
    const {payload: [params], result} = FILTERS_CLIENT_TO_SERVER_MOCK;

    expect(filtersFromClientToServer(params)).toStrictEqual(result);
});

test('prepareChartFiltersToRequest converts correctly', () => {
    const {payload: [params, options], result} = PREPARE_CHART_FILTERS_MOCK;

    expect(prepareChartFiltersToRequest(params, options)).toStrictEqual(result);
});

test('prepareChartFiltersToRequest with shiftConfirmationMode "all" contain shift_drafts entity', () => {
    const {payload: [params], result} = PREPARE_CHART_FILTERS_MOCK;

    expect(prepareChartFiltersToRequest(params, {shiftConfirmationMode: ShiftConfirmationMode.All}).load_entities)
        .toStrictEqual([...result.load_entities!, 'shift_drafts']);
});

test('prepareDisciplineFiltersToRequest converts correctly', () => {
    const {payload: [params], result} = PREPARE_DISCIPLINE_FILTERS_MOCK;

    expect(prepareDisciplineFiltersToRequest(params)).toStrictEqual(result);
});

test('convertBreaks with breaks converts correctly', () => {
    const {payload: [form], result} = CONVERT_BREAKS_MOCK;

    expect(convertBreaks(form)).toStrictEqual(result);
});

test('convertBreaks with spreadBreaks return undefined', () => {
    const {payload: [form]} = CONVERT_BREAKS_MOCK;

    expect(convertBreaks({
        ...form,
        spread_breaks: true,
    })).toStrictEqual(undefined);
});

test('prepareOperatorsShift converts correctly', () => {
    const {payload: [shift, editShiftForm, operator], result} = PREPARE_OPERATORS_SHIFT_MOCK;

    expect(prepareOperatorsShift(shift, editShiftForm, operator)).toStrictEqual(result);
});

test('prepareOperatorsShift without operator trying get info from editShiftForm and has empty operator info', () => {
    const {payload: [shift, editShiftForm], result} = PREPARE_OPERATORS_SHIFT_MOCK;
    // eslint-disable-next-line
    const {full_name, schedules, ...rest} = result;

    expect(prepareOperatorsShift(shift, editShiftForm)).toStrictEqual({
        ...rest,
        frozen: false,
        revision_id: '',
        yandex_uid: '',
    });
});

test('updateOperatorsShiftWithForm fill and update operatorsShift by editShiftForm', () => {
    const {payload: [shift, editShiftForm, operator]} = PREPARE_OPERATORS_SHIFT_MOCK;
    const operatorsShift = prepareOperatorsShift(shift, editShiftForm, operator);

    expect(updateOperatorsShiftWithForm(
        operatorsShift,
        {
            ...editShiftForm,
            is_additional: true,
            spread_breaks: true,
        },
    )).toStrictEqual({
        ...operatorsShift,
        breaks: undefined,
        events: [],
        type: 'additional',
    });
});

test('convertWorkBreakToServer converts correctly', () => {
    const {breaks} = EDIT_SHIFT_FORM_MOCK;
    const {result} = PREPARE_OPERATORS_SHIFT_MOCK;

    expect(convertWorkBreakToServer(breaks![0])).toStrictEqual(result.breaks![0]);
});

test('convertProjectActivityToServer converts correctly', () => {
    const {payload: [projectActivity], result} = CONVERT_PA_TO_SERVER_MOCK;

    expect(convertProjectActivityToServer(projectActivity)).toStrictEqual(result);
});

test('prepareShiftForSaveRequest converts correctly', () => {
    const {payload: [shift, editShiftForm, operator], result} = PREPARE_SHIFT_FOR_SAVE_MOCK;

    expect(prepareShiftForSaveRequest(shift, editShiftForm, operator)).toStrictEqual(result);
});

test('convertTableShiftToServerShift converts correctly', () => {
    const {payload: [tableShift], result} = CONVERT_TABLE_SHIFT_TO_SERVER_MOCK;

    expect(convertTableShiftToServerShift(tableShift)).toStrictEqual(result);
});

test('convertPeriodForRequest converts correctly', () => {
    const {payload: [period], result} = CONVERT_PERIOD_FOR_REQUEST_MOCK;

    expect(convertPeriodForRequest(period)).toStrictEqual(result);
});

test('convertPeriodForRequest without period return today start/end', () => {
    expect(convertPeriodForRequest()).toStrictEqual({
        datetime_from: moment().startOf('day').format(),
        datetime_to: moment().endOf('day').format(),
    });
});

test('normalizeShiftsPayload remove empty values', () => {
    const {payload: [data], result} = NORMALIZE_SHIFTS_PAYLOAD_MOCK;

    expect(normalizeShiftsPayload(data)).toStrictEqual(result);
});
