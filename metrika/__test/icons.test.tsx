import React, { createElement, FC } from 'react';

import { iconGroups, IconsGroup } from '../icons.stories';
import { makeScreenshot } from '../../../../test-utils/screenshot';

const icons = iconGroups.reduce((prev: IconsGroup[], cur) => {
    return prev.concat(cur.icons);
}, []);

describe('Icons', () => {
    describe.each(icons)('screenshot', ({ iconsGroup, name }) =>
        it(`make screenshot ${name || ''}`, async () => {
        const Component: FC = () => (
            <>
                {createElement(iconsGroup({ fill: 'black' }))}
                {createElement(iconsGroup({ fill: 'red' }))}
            </>
        );
        await makeScreenshot(<Component />);
    })
    );
});
