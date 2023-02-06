import * as React from 'react';
import { cleanup } from 'react-testing-library';
import { ShowMoreRow } from '..';
import { jestSnapshotRenderTest } from 'utils/jest-utils';

afterEach(cleanup);

const Table = (props: React.PropsWithChildren<{}>) => (
    <table>
        <tbody>
            <tr>{props.children}</tr>
        </tbody>
    </table>
);

jestSnapshotRenderTest({
    'without expand': (
        <Table>
            <ShowMoreRow
                size="s"
                cellsCount={3}
                total={30}
                offset={15}
                expandable={false}
                loading={false}
                onClick={() => undefined}
            />
        </Table>
    ),
    'with expand': (
        <Table>
            <ShowMoreRow
                size="s"
                cellsCount={3}
                total={30}
                offset={15}
                expandable={true}
                loading={false}
                onClick={() => undefined}
            />
        </Table>
    ),
});
