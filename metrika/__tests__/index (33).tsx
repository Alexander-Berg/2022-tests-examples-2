import React from 'react';
import { cleanup } from 'react-testing-library';
import { Humanize } from '..';
import { jestSnapshotRenderTest } from 'client/utils/jest-utils';

afterEach(cleanup);

const snapshotsMap = {
    'percent null': <Humanize value={null} type="percentage" />,
    'percent undefined': <Humanize value={undefined} type="percentage" />,
    'percent negative': <Humanize value={-10} type="percentage" />,
    'percent positive': <Humanize value={10} type="percentage" />,
    'percent too high': <Humanize value={1000000} type="percentage" />,
    'percent too low': <Humanize value={0.001} type="percentage" />,
    'int null': <Humanize value={null} type="number" />,
    'int undefined': <Humanize value={undefined} type="number" />,
    'int negative': <Humanize value={-10} type="number" />,
    'int positive': <Humanize value={10} type="number" />,
    'int too high': <Humanize value={1000000} type="number" />,
    'int too high compress': (
        <Humanize compress value={1000000} type="number" />
    ),
    'int too low': <Humanize value={0.001} type="number" />,
    'float null': <Humanize value={null} type="float" />,
    'float undefined': <Humanize value={undefined} type="float" />,
    'float negative': <Humanize value={-10} type="float" />,
    'float positive': <Humanize value={10} type="float" />,
    'float too high': <Humanize value={1000000} type="float" />,
    'float too low': <Humanize value={0.001} type="float" />,
    'float too low negative': <Humanize value={-0.001} type="float" />,
};

jestSnapshotRenderTest(snapshotsMap);
