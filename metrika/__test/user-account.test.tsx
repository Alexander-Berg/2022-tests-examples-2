import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import * as React from 'react';

import {
    View,
    Representative,
    HiddenDisplayName,
    HiddenDisplayNameRepresentative,
    SmallWidth,
    EmptyAvatarBoth,
    EmptyAvatarRepresentative,
    EmptyAvatarUser,
} from '../user-account.stories';

describe('UserAccount', () => {
    describe('screenshot', () => {
        it('view', async () => {
            await makeScreenshot(<View />, { width: 1000, height: 400 });
        });
        it('representative', async () => {
            await makeScreenshot(<Representative />, { width: 700, height: 400 });
        });
        it('hidden display name', async () => {
            await makeScreenshot(<HiddenDisplayName />, { width: 500, height: 400 });
        });
        it('hidden display name representative', async () => {
            await makeScreenshot(<HiddenDisplayNameRepresentative />, { width: 700, height: 400 });
        });
        it('small width', async () => {
            await makeScreenshot(<SmallWidth />, { width: 500, height: 400 });
        });
        it('empty avatar both', async () => {
            await makeScreenshot(<EmptyAvatarBoth />, { width: 1000, height: 400 });
        });
        it('empty avatar representative', async () => {
            await makeScreenshot(<EmptyAvatarRepresentative />, { width: 1000, height: 400 });
        });
        it('empty avatar user', async () => {
            await makeScreenshot(<EmptyAvatarUser />, { width: 1000, height: 400 });
        });
    });
});
