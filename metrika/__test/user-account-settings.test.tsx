import React from 'react';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import userEvent from '@testing-library/user-event';
import { fireEvent, render, screen } from '@testing-library/react';
import { KeyboardKey } from '@client-libs/keyboard/keyboard-key';
import {
    TestSelectedRepresentativeAccount,
    TestWithRepresentativeAccounts,
    WithTestContext,
} from '@client-libs/mindstorms/components/user-account-settings/user-account-settings.stories';
import { UserAccountSettingsProps } from '@client-libs/mindstorms/components/user-account-settings/user-account-settings-props';
import { UserAccountSettings } from '@client-libs/mindstorms/components/user-account-settings/user-account-settings';
import { fillObject } from '@shared/utils/type-utils';
import { UserAccountEntity } from '@shared/analytics-dto/entities/user';

const onSelectPersonalAccount = jest.fn();
const onSelectRepresentativeAccount = jest.fn();

const accounts = [
    fillObject(new UserAccountEntity(), {
        uid: '1',
        displayName: 'test name',
        login: 'fist-login',
        avatarSrc: '',
    }),
    fillObject(new UserAccountEntity(), {
        uid: '2',
        login: 'second-login',
        displayName: 'second name',
        avatarSrc: '',
    }),
];

const representativeAccounts = [
    fillObject(new UserAccountEntity(), {
        uid: '1',
        login: 'first-representative',
        displayName: 'representative name',
        avatarSrc: '',
    }),
    fillObject(new UserAccountEntity(), {
        uid: '2',
        login: 'second-representative',
        displayName: 'second representative name',
        avatarSrc: '',
    }),
];

function renderUserAccountSettings(props?: Partial<UserAccountSettingsProps>): void {
    render(
        <UserAccountSettings
            isLoading={false}
            selectedAccount={accounts[0]}
            representativeAccounts={representativeAccounts}
            accounts={accounts}
            onSelectRepresentativeAccount={onSelectRepresentativeAccount}
            onSelectPersonalAccount={onSelectPersonalAccount}
            {...props}
        />
    );
}

const clickByText = (text: string, position?: number): void => {
    const element = position !== undefined ? screen.getAllByText(text)[position] : screen.getByText(text);
    userEvent.click(element);
};

const emulateKeyboardEvent = (key: KeyboardKey): void => {
    const focusedElement = document.activeElement!;
    fireEvent.keyDown(focusedElement, { key });
};

describe('user-account-settings', () => {
    describe('screenshot', () => {
        it('test user accounts', async () => {
            await makeScreenshot(<WithTestContext />, { height: 600, width: 1201 });
        });

        it('with representative accounts', async () => {
            await makeScreenshot(<TestWithRepresentativeAccounts />, { height: 600, width: 1201 });
        });

        it('with selected representative account', async () => {
            await makeScreenshot(<TestSelectedRepresentativeAccount />, { height: 600, width: 1201 });
        });
    });

    describe('logic', () => {
        describe('user account settings', () => {
            beforeAll(() => {
                window.HTMLFormElement.prototype.submit = (): null => null;
            });

            beforeEach(() => {
                jest.clearAllMocks();
            });

            it('should open and close user settings', () => {
                const selectedAccount = accounts[0];
                renderUserAccountSettings({
                    selectedAccount: selectedAccount,
                });

                clickByText(selectedAccount.login);

                expect(screen.getByTestId('user-menu-popup-content')).toBeInTheDocument();

                clickByText(selectedAccount.login, 0);
                expect(screen.queryByTestId('user-menu-popup-content')).not.toBeInTheDocument();
            });

            it('should select account and close user settings', () => {
                const selectedAccount = accounts[0];
                const newAccount = accounts[1];
                renderUserAccountSettings({
                    selectedAccount: selectedAccount,
                });

                // open popup
                clickByText(selectedAccount.login);

                // select new account
                clickByText(newAccount.login);

                expect(screen.queryByText(newAccount.login)).not.toBeInTheDocument();
                expect(onSelectPersonalAccount).toBeCalledWith(newAccount.uid);
            });

            it('should start navigation in personal accounts when representative account is not selected', () => {
                const selectedAccount = accounts[0];
                renderUserAccountSettings({
                    selectedAccount: selectedAccount,
                    selectedRepresentativeAccount: undefined,
                });

                // open popup
                clickByText(selectedAccount.login);

                emulateKeyboardEvent(KeyboardKey.Down);
                emulateKeyboardEvent(KeyboardKey.Enter);

                expect(onSelectPersonalAccount).toBeCalledWith(accounts[0].uid);
            });

            it('should start navigation in representative accounts when representative account is selected', () => {
                const selectedAccount = accounts[0];
                const selectedRepresentativeAccount = representativeAccounts[0];
                renderUserAccountSettings({
                    selectedAccount: selectedAccount,
                    selectedRepresentativeAccount: selectedRepresentativeAccount,
                });

                // open popup
                clickByText(selectedAccount.login);

                emulateKeyboardEvent(KeyboardKey.Down);
                emulateKeyboardEvent(KeyboardKey.Enter);

                expect(onSelectPersonalAccount).not.toBeCalled();
                expect(onSelectRepresentativeAccount).toBeCalledWith(representativeAccounts[0].uid);
            });

            it('should select current personal account by click on the footer button', () => {
                const selectedAccount = accounts[0];
                renderUserAccountSettings({
                    selectedAccount: selectedAccount,
                    selectedRepresentativeAccount: representativeAccounts[0],
                });

                // open popup
                clickByText(selectedAccount.login);

                userEvent.click(screen.getByTestId('user-accounts-footer-button'));
                expect(onSelectPersonalAccount).toBeCalledWith(selectedAccount.uid);
            });

            it('should delegate navigation from representative account to personal by pressing `right` on keyboard', () => {
                const selectedAccount = accounts[0];
                renderUserAccountSettings({
                    selectedAccount: selectedAccount,
                    selectedRepresentativeAccount: representativeAccounts[0],
                });

                // open popup
                clickByText(selectedAccount.login);

                emulateKeyboardEvent(KeyboardKey.Right);
                emulateKeyboardEvent(KeyboardKey.Enter);

                expect(onSelectPersonalAccount).toBeCalledWith(selectedAccount.uid);
            });

            it('should select hovering account by pressing `enter` on keyboard', () => {
                const selectedAccount = accounts[0];
                const representativeAccount = representativeAccounts[1];
                renderUserAccountSettings({
                    selectedAccount: selectedAccount,
                    selectedRepresentativeAccount: undefined,
                });

                clickByText(selectedAccount.login);

                fireEvent.mouseEnter(screen.getByText(representativeAccount.login));
                emulateKeyboardEvent(KeyboardKey.Enter);

                expect(onSelectRepresentativeAccount).toBeCalledWith(representativeAccount.uid);
            });
        });
    });
});
