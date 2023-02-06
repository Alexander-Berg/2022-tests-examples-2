import { getReportsMenu, getReportsByGroup } from '..';

test('Expected menu fragment for no-agency external user', () => {
    expect(
        getReportsMenu({
            permission: 'view',
            isNda: false,
            applicationFeatures: [],
        }),
    ).toEqual(
        expect.arrayContaining([
            [
                { id: 'technical', type: 'group' },
                { id: 'crashes', type: 'group' },
                { id: 'errors', type: 'group' },
            ],
        ]),
    );
});

test('Expected menu fragment for no-agency internal user', () => {
    expect(
        getReportsByGroup({
            groupId: 'crashes',
            permission: 'edit',
            isNda: true,
            applicationFeatures: [],
        }),
    ).toEqual(
        expect.arrayContaining([
            { id: 'crash-logs-android', type: 'report' },
            { id: 'crash-logs-ios', type: 'report' },
        ]),
    );
});

test('Expected menu fragment for agency external user', () => {
    expect(
        getReportsByGroup({
            groupId: 'crashes',
            permission: 'agency_view',
            isNda: false,
            applicationFeatures: [],
        }),
    ).toEqual([]);
});

test('Expected menu fragment for agency internal user', () => {
    expect(
        getReportsByGroup({
            groupId: 'crashes',
            permission: 'agency_edit',
            isNda: true,
            applicationFeatures: [],
        }),
    ).toEqual([]);
});
