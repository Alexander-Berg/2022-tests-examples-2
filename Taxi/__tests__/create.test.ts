import moment from 'moment-timezone';

import SettingsApi from 'api/app/settings';

import {
    currentOffsetMinutes,
    currentOffsetHours,
    localDateFromUtcNow,
    localDateFromUtc,
} from '../create';

beforeEach(() => {
    moment.tz.setDefault(SettingsApi.DEFAULT_TIMEZONE);
});

test('currentOffsetMinutes return default TZ offset minutes', () => {
    expect(currentOffsetMinutes()).toEqual(180);
});

test('currentOffsetMinutes return Samara TZ offset minutes', () => {
    moment.tz.setDefault('Europe/Samara');
    expect(currentOffsetMinutes()).toEqual(240);
});

test('currentOffsetHours return default TZ offset hours', () => {
    expect(currentOffsetHours()).toEqual(3);
});

test('currentOffsetHours return Samara TZ offset hours', () => {
    moment.tz.setDefault('Europe/Samara');
    expect(currentOffsetHours()).toEqual(4);
});

// Другие тесты этой функции могут быть неустойчивы из-за времени запуска
test('localDateFromUtcNow return same date with UTC TZ', () => {
    moment.tz.setDefault('UTC');
    const now = moment().startOf('minute');

    expect(localDateFromUtcNow().startOf('minute').isSame(now)).toEqual(true);
});

test('localDateFromUtc return correct datetime for default TZ', () => {
    expect(localDateFromUtc('2021-12-23T15:00:00').format()).toEqual('2021-12-23T18:00:00Z');
});
