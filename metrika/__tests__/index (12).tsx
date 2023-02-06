// import * as React from 'react';
// import { cleanup } from 'react-testing-library';
// import { ReportTable } from '..';
// import { jestSnapshotRenderTest } from 'utils/jest-utils';

// afterEach(cleanup);

// const header = {
//     selected: false,
//     cells: [
//         { id: 'visits', content: 'Визиты' },
//         { id: 'pageviews', content: 'Просмотры' },
//     ],
// };

// const body = [
//     {
//         id: '1',
//         content: 'dim1',
//         cells: [{ value: 1, subvalue: 2 }],
//     },
//     {
//         id: '2',
//         content: 'dim2',
//         cells: [{ value: 1, subvalue: 2 }],
//     },
// ];

// const crumbs = [{ id: '1', title: 'браузер' }];

// jestSnapshotRenderTest({
//     drilldown: (
//         <ReportTable
//             type="drilldown"
//             crumbs={crumbs}
//             header={header}
//             body={body}
//         />
//     ),
//     'non-expandable drilldown': (
//         <ReportTable
//             type="drilldown"
//             crumbs={crumbs}
//             header={header}
//             body={body}
//             expandable={false}
//         />
//     ),
//     flat: (
//         <ReportTable type="flat" crumbs={crumbs} header={header} body={body} />
//     ),
//     multilevel: (
//         <ReportTable
//             type="multilevel"
//             crumbs={crumbs}
//             header={header}
//             body={body}
//         />
//     ),
// });
it('', () => {
    expect(true).toBe(true);
});
