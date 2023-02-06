import * as React from 'react';

import { makeScreenshot } from '@metrika/ui/utils/jest/makeScreenshot';

import { Main } from '../ErrorMessage.stories';

describe('ErrorMessage', () => {
    it('screenshooter', async () => {
        await makeScreenshot(<Main />);
    });
});
