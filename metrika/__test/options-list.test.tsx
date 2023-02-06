import React from 'react';
import {
    DefaultOptionListItem,
    OptionsListProps,
} from '@client-libs/mindstorms/components/options-list/options-list-props';
import { fireEvent, render, screen } from '@testing-library/react';
import { CustomItems, Disabled, Main } from '@client-libs/mindstorms/components/options-list/options-list.stories';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom/extend-expect';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import { OptionsList } from '@client-libs/mindstorms/components/options-list/options-list';

const items: DefaultOptionListItem[] = [
    { title: 'Сегодня', id: '1' },
    { title: 'Вчера', id: '2' },
    { title: 'Неделя', id: '3' },
];
const selectedItem = items[1];
const firstItem = items[0];
const thirdItem = items[2];

function findItemByTitle(title: string): Element {
    return screen.getByText(title);
}

function selectItem(element: Element): void {
    userEvent.click(element);
}

function moveToItemAndSelect(direction: 'Down' | 'Up'): void {
    const focusedElement = document.activeElement!;
    fireEvent.keyDown(focusedElement, { key: direction });
    fireEvent.keyDown(focusedElement, { key: 'Enter' });
}

const onSelect = jest.fn();

function renderOptionsList(props?: Partial<OptionsListProps>): void {
    render(<OptionsList items={items} onSelect={onSelect} selectedIds={[selectedItem.id]} {...props} />);
}

describe('OptionsList', () => {
    describe('screenshot', () => {
        it('default', async () => {
            await makeScreenshot(<Main />, { width: 308, height: 308 });
        });

        it('custom', async () => {
            await makeScreenshot(<CustomItems />, { width: 308, height: 308 });
        });

        it('disabled', async () => {
            await makeScreenshot(<Disabled />, { width: 308, height: 308 });
        });
    });

    describe('logic', () => {
        beforeEach(() => {
            onSelect.mockClear();
        });

        describe('select item', () => {
            beforeEach(() => {
                renderOptionsList();
            });

            it('should change selected item', () => {
                const firstElem = findItemByTitle(firstItem.title.toString());
                selectItem(firstElem);

                expect(onSelect).toBeCalledWith([firstItem.id]);
            });

            it('should unselect selected item', () => {
                const selectedElem = findItemByTitle(selectedItem.title.toString());
                selectItem(selectedElem);
                expect(onSelect).toBeCalledWith([]);
            });
        });

        describe('multiple select', () => {
            beforeEach(() => {
                renderOptionsList({ isMultiple: true });
            });

            it('should select several items', () => {
                const firstElem = findItemByTitle(firstItem.title.toString());
                selectItem(firstElem);
                expect(onSelect).toBeCalledWith([firstItem.id, selectedItem.id]);
            });
        });

        describe('navigation', () => {
            it('should move to the element with the `down` key and select it by pressing enter', () => {
                renderOptionsList();
                moveToItemAndSelect('Down');
                expect(onSelect).toBeCalledWith([thirdItem.id]);
            });

            it('should move to the element with the `up` key and select it by pressing enter', () => {
                renderOptionsList();
                moveToItemAndSelect('Up');
                expect(onSelect).toBeCalledWith([firstItem.id]);
            });

            it('should move to the first element with the `down` key after last active element', () => {
                renderOptionsList({
                    selectedIds: [items[items.length - 1].id],
                });
                moveToItemAndSelect('Down');
                expect(onSelect).toBeCalledWith([firstItem.id]);
            });

            it('should move to the last element with the `up` key after first active element', () => {
                renderOptionsList({ selectedIds: [firstItem.id] });
                moveToItemAndSelect('Up');
                expect(onSelect).toBeCalledWith([items[items.length - 1].id]);
            });
        });

        describe('disabled item', () => {
            const disabledTitle = 'disabled';
            beforeEach(() => {
                const itemsWithDisabled = items.map((item, index) => {
                    if (index === 1) {
                        return {
                            ...item,
                            title: disabledTitle,
                            isDisabled: true,
                        };
                    }
                    return item;
                });
                renderOptionsList({ items: itemsWithDisabled, selectedIds: [] });
            });

            it('shouldn`t selected disabled item', () => {
                const disabledItem = findItemByTitle(disabledTitle);
                selectItem(disabledItem);

                expect(onSelect).not.toBeCalled();
            });

            it('shouldn`t selected disabled item by pressed enter', () => {
                moveToItemAndSelect('Down');
                expect(onSelect).not.toBeCalled();
            });
        });
    });
});
