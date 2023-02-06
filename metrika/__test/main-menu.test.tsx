import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import React from 'react';
import {
    Compact,
    Loading,
    Main,
    TestExample,
    WithAdditionalItems,
    WithLinkItems,
} from '@client-libs/mindstorms/components/main-menu/main-menu.stories';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { MainMenu } from '@client-libs/mindstorms/components/main-menu/main-menu';
import userEvent from '@testing-library/user-event';
import { MainMenuItemType, MainMenuProps } from '@client-libs/mindstorms/components/main-menu/main-menu-props';

const onToggle = jest.fn();
const onClick = jest.fn();

const enum MenuItem {
    NestedRoot1 = 'NestedRoot1',
    NestedRoot2 = 'NestedRoot2',
    ClickableRoot = 'ClickableRoot',
    ClickableDefault1 = 'ClickableDefault1',
    ClickableDefault2 = 'ClickableDefault2',
}

const items: MainMenuProps['items'] = {
    [MenuItem.NestedRoot1]: {
        title: 'root 1',
        type: MainMenuItemType.Nested,
        groups: [{ itemsIds: [MenuItem.ClickableDefault1] }],
    },
    [MenuItem.NestedRoot2]: {
        title: 'root 2',
        type: MainMenuItemType.Nested,
        groups: [{ itemsIds: [MenuItem.ClickableDefault2] }],
    },
    [MenuItem.ClickableRoot]: {
        title: 'clickable root',
        type: MainMenuItemType.Clickable,
        onClick,
    },
    [MenuItem.ClickableDefault1]: {
        title: 'nested 1',
        type: MainMenuItemType.Clickable,
        onClick,
    },
    [MenuItem.ClickableDefault2]: {
        title: 'nested 2',
        type: MainMenuItemType.Clickable,
        onClick,
    },
};

const rootItemsIds = [[MenuItem.NestedRoot1, MenuItem.NestedRoot2, MenuItem.ClickableRoot]];

function renderMainMenu(props?: Partial<MainMenuProps>): void {
    render(<MainMenu items={items} rootItemIds={rootItemsIds} onToggle={onToggle} {...props} />);
}

function emulateClick(title: string): void {
    userEvent.click(screen.getByText(title));
}

describe('MainMenu', () => {
    describe('screenshot', () => {
        it('default', async () => {
            await makeScreenshot(<Main />, { width: 200, height: 400 });
        });

        it('small height', async () => {
            await makeScreenshot(
                <div style={{ overflow: 'hidden', height: '150px' }}>
                    <Main />
                </div>,
                { width: 200, height: 200 }
            );
        });

        it('closed', async () => {
            await makeScreenshot(<Compact />, { width: 200, height: 400 });
        });

        it('with nested', async () => {
            await makeScreenshot(<TestExample />, {
                width: 400,
                height: 400,
            });
        });

        it('with additional itemsIds', async () => {
            await makeScreenshot(<WithAdditionalItems />, {
                width: 600,
                height: 400,
            });
        });

        it('loading', async () => {
            await makeScreenshot(<Loading />, {
                width: 600,
                height: 400,
            });
        });

        it('link items', async () => {
            await makeScreenshot(<WithLinkItems />, {
                width: 400,
                height: 400,
            });
        });
    });

    describe('logic', () => {
        beforeEach(() => {
            jest.useFakeTimers();
            onClick.mockClear();
        });

        it('should toggle menu', () => {
            renderMainMenu({ isCompact: true });

            userEvent.click(screen.getByTestId('main-menu-toggle'));
            expect(onToggle).toBeCalledWith(false);
        });

        it('should call item onClick after select clickable item', () => {
            renderMainMenu();

            emulateClick(items[MenuItem.ClickableRoot].title);
            expect(onClick).toBeCalledWith(MenuItem.ClickableRoot);
        });

        it('should open nested content after select nested item', () => {
            renderMainMenu();

            const rootTitle = items[MenuItem.NestedRoot1].title;
            const nestedTitle = items[MenuItem.ClickableDefault1].title;

            expect(screen.queryByText(nestedTitle)).not.toBeInTheDocument();

            emulateClick(rootTitle);

            act(() => {
                jest.runAllTimers();
            });

            expect(screen.queryByText(nestedTitle)).toBeInTheDocument();
        });

        it('should open nested content by mouseEnter for not root nested item', () => {
            const rootTitle = 'root';
            const secondTitle = 'nested 1';
            const thirdTitle = 'nested 2';
            renderMainMenu({
                rootItemIds: [['0']],
                items: {
                    0: {
                        title: rootTitle,
                        type: MainMenuItemType.Nested,
                        groups: [{ itemsIds: ['1'] }],
                    },
                    1: {
                        title: secondTitle,
                        type: MainMenuItemType.Nested,
                        groups: [{ itemsIds: ['2'] }],
                    },
                    2: {
                        title: thirdTitle,
                        type: MainMenuItemType.Clickable,
                        onClick,
                    },
                },
            });

            emulateClick(rootTitle);

            expect(screen.queryByText(thirdTitle)).not.toBeInTheDocument();

            fireEvent.mouseEnter(screen.getByText(secondTitle));
            act(() => {
                jest.runAllTimers();
            });

            expect(screen.queryByText(thirdTitle)).toBeInTheDocument();
        });

        it('should close nested content after repeated select root nested item', () => {
            renderMainMenu();

            const rootTitle = items[MenuItem.NestedRoot1].title;
            const nestedTitle = items[MenuItem.ClickableDefault1].title;

            // open
            emulateClick(rootTitle);
            expect(screen.queryByText(nestedTitle)).toBeInTheDocument();

            // close
            emulateClick(nestedTitle);

            act(() => {
                jest.runAllTimers();
            });

            expect(screen.queryByText(nestedTitle)).not.toBeInTheDocument();
        });

        it('shouldn`t close nested content after repeated select not root nested item', () => {
            const rootTitle = 'root';
            const secondTitle = 'nested 1';
            const thirdTitle = 'nested 2';
            renderMainMenu({
                rootItemIds: [['0']],
                items: {
                    0: {
                        title: rootTitle,
                        type: MainMenuItemType.Nested,
                        groups: [{ itemsIds: ['1'] }],
                    },
                    1: {
                        title: secondTitle,
                        type: MainMenuItemType.Nested,
                        groups: [{ itemsIds: ['2'] }],
                    },
                    2: {
                        title: thirdTitle,
                        type: MainMenuItemType.Clickable,
                        onClick,
                    },
                },
            });

            // click root item
            emulateClick(rootTitle);

            // click nested item
            emulateClick(secondTitle);
            act(() => {
                jest.runAllTimers();
            });

            expect(screen.queryByText(thirdTitle)).toBeInTheDocument();

            // repeated click nested item
            emulateClick(secondTitle);
            act(() => {
                jest.runAllTimers();
            });

            expect(screen.queryByText(thirdTitle)).toBeInTheDocument();
        });

        it('should close nested content after outside click', () => {
            renderMainMenu();

            const rootTitle = items[MenuItem.NestedRoot1].title;
            const nestedTitle = items[MenuItem.ClickableDefault1].title;

            emulateClick(rootTitle);
            expect(screen.queryByText(nestedTitle)).toBeInTheDocument();

            fireEvent.click(document.body);
            act(() => {
                jest.runAllTimers();
            });

            expect(screen.queryByText(nestedTitle)).not.toBeInTheDocument();
        });

        it('should close popups after click on item without nested content', () => {
            renderMainMenu();

            const rootTitle = items[MenuItem.NestedRoot1].title;
            const nestedTitle = items[MenuItem.ClickableDefault1].title;

            emulateClick(rootTitle);
            expect(screen.queryByText(nestedTitle)).toBeInTheDocument();

            emulateClick(nestedTitle);

            act(() => {
                jest.runAllTimers();
            });

            expect(screen.queryByText(nestedTitle)).not.toBeInTheDocument();
        });

        it('should open all nested content by click on root item if items are active', () => {
            const rootTitle = 'root';
            const secondTitle = 'nested 1';
            const thirdTitle = 'nested 2';
            renderMainMenu({
                rootItemIds: [['0']],
                items: {
                    0: {
                        title: rootTitle,
                        isActive: true,
                        type: MainMenuItemType.Nested,
                        groups: [{ itemsIds: ['1'] }],
                    },
                    1: {
                        isActive: true,
                        title: secondTitle,
                        type: MainMenuItemType.Nested,
                        groups: [{ itemsIds: ['2'] }],
                    },
                    2: {
                        isActive: true,
                        title: thirdTitle,
                        type: MainMenuItemType.Clickable,
                        onClick,
                    },
                },
            });

            expect(screen.queryByText(secondTitle)).not.toBeInTheDocument();

            emulateClick(rootTitle);
            act(() => {
                jest.runAllTimers();
            });

            expect(screen.queryByText(secondTitle)).toBeInTheDocument();
            expect(screen.queryByText(thirdTitle)).toBeInTheDocument();
        });

        it('should open new nested content after select another nested item', () => {
            renderMainMenu();

            const firstRootTitle = items[MenuItem.NestedRoot1].title;
            const secondRootTitle = items[MenuItem.NestedRoot2].title;
            const firstNestedTitle = items[MenuItem.ClickableDefault1].title;
            const secondNestedTitle = items[MenuItem.ClickableDefault2].title;

            emulateClick(firstRootTitle);
            expect(screen.queryByText(firstNestedTitle)).toBeInTheDocument();

            emulateClick(secondRootTitle);

            expect(screen.queryByText(firstNestedTitle)).not.toBeInTheDocument();
            expect(screen.queryByText(secondNestedTitle)).toBeInTheDocument();
        });
    });
});
