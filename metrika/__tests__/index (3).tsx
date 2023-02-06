import * as React from 'react';
import { cleanup } from 'react-testing-library';
import { BreadCrumbs } from '..';
import { jestSnapshotRenderTest } from 'utils/jest-utils';

afterEach(cleanup);

const crumbsItems = [{ title: 'Браузер' }, { title: 'Версия браузера' }].map(
    (item, index) => ({ ...item, id: String(index) }),
);

const crumbsItemsWithSubtitle = crumbsItems.map((item, index, arr) => ({
    ...item,
    subtitle: index === arr.length - 1 ? undefined : 'Chrome',
}));

jestSnapshotRenderTest({
    selectable: <BreadCrumbs items={crumbsItemsWithSubtitle} />,
    'not selectable': (
        <BreadCrumbs items={crumbsItemsWithSubtitle} selectable={false} />
    ),
    'without subtitle': <BreadCrumbs items={crumbsItems} />,
    'without subtitle not selectable': (
        <BreadCrumbs items={crumbsItems} selectable={false} />
    ),
});

/**
 * jsdom не рендерит layout на самом деле, там все размеры нулевые
 * нужно попробовать puppeteer
 */
// describe('поведение в родительский контейнерах', () => {
//     it('сокращается в контейнерах с маленькой шириной', async () => {
//         const { getByTestId } = render(
//             <div style={{ width: '200px' }}>
//                 <BreadCrumbs items={crumbsItemsWithSubtitle} />
//             </div>,
//         );

//         await wait(() => expect(getByTestId('anchor')).toHaveStyleRule('opacity', '1'));
//     });
// });
