import { fireEvent, render, screen, act } from '@testing-library/react';
import * as React from 'react';
import { ReactElement } from 'react';
import { GroupItemSelectProps, GroupSelectorKind } from '../group-item-select-props';
import { generateGroups, withoutGroupTitle } from '../__mock/groups';
import { GroupItemSelect } from '../group-item-select';
import { MockSearchItemComponent } from '../__mock/search-item-component';
import { MockItemComponent } from '../__mock/item-component';
import { getTextWidth } from '../../../../string-utils/text-width';
import { searchInputTestId } from '../__internal/select-dropdown';
import userEvent from '@testing-library/user-event';

jest.mock(
    'react-virtualized-auto-sizer',
    () =>
        ({ children }: { children: (d: { height: number; width: number }) => ReactElement }): ReactElement =>
            children({ height: 600, width: 600 })
);

jest.mock('../../../../string-utils/text-width');
(getTextWidth as unknown as jest.Mock<typeof getTextWidth>).mockReturnValue(() => 100);

jest.useFakeTimers();

const mockSelectGroup = jest.fn();
const mockSelectItem = jest.fn();
const mockSearch = jest.fn();
const mockFetchItem = jest.fn();
const mockGetItemId = jest.fn();

function renderGroupItemSelect(customProps?: Partial<GroupItemSelectProps<string>>): void {
    const props: GroupItemSelectProps<string> = {
        isLoading: false,
        searchItemComponent: MockSearchItemComponent,
        itemComponent: MockItemComponent,
        valueViewContent: 'value',
        groups: generateGroups(10),
        itemHeight: 50,
        itemsColumnWidth: 240,
        getItemId: mockGetItemId,
        onSelectItem: mockSelectItem,
        fetchItem: mockFetchItem,
        onSearch: mockSearch,
        onSelectGroup: mockSelectGroup,
        selectedItemId: '1',
        data: { items: [] },
        ...customProps,
    };

    if (!props.isLoading && !(customProps && 'data' in customProps && customProps.data)) {
        props.data = { selectedGroup: props.groups?.[0], items: [] };
    }

    render(<GroupItemSelect {...props} />);
}

function openDropdown(): void {
    fireEvent.click(screen.getByTestId('dp-anchor'));
    jest.advanceTimersByTime(100);
}

describe('GroupItemSelect', () => {
    beforeEach(() => {
        mockGetItemId.mockClear();
        mockSelectItem.mockClear();
        mockFetchItem.mockClear();
        mockSearch.mockClear();
        mockSelectGroup.mockClear();
    });

    it('should invoke onSelectGroup', () => {
        renderGroupItemSelect();
        act(() => {
            openDropdown();
        });
        act(() => {
            fireEvent.click(screen.getByText(withoutGroupTitle));
        });
        expect((mockSelectGroup.mock.calls[0] as Array<unknown>)[0]).toMatchObject({
            kind: GroupSelectorKind.WithoutGroup,
        });
    });

    it('should invoke onFetchItem', () => {
        const itemsCount = 3;
        renderGroupItemSelect({
            data: {
                selectedGroup: { kind: GroupSelectorKind.All },
                items: new Array(itemsCount),
            },
        });
        act(() => {
            openDropdown();
        });
        expect(mockFetchItem).toBeCalledTimes(itemsCount);
    });

    it("shouldn't render search input for single group containing less than 6 items", () => {
        const itemsCount = 5;
        renderGroupItemSelect({
            groups: [{ kind: GroupSelectorKind.All, title: 'All' }],
            data: {
                selectedGroup: { kind: GroupSelectorKind.All },
                items: new Array(itemsCount),
            },
        });
        act(() => {
            openDropdown();
        });
        expect(screen.queryAllByTestId(searchInputTestId)).toEqual([]);
    });

    it('should render search input for multiple group', () => {
        renderGroupItemSelect();
        act(() => {
            openDropdown();
        });
        expect(screen.queryAllByTestId(searchInputTestId).length).toBe(1);
    });

    it('should call onSearch when search input has changed', () => {
        renderGroupItemSelect();
        act(() => {
            openDropdown();
        });
        // to focus input
        userEvent.click(document.querySelector('.text-input__icon')!);
        userEvent.keyboard('s');
        expect(mockSearch).toBeCalledWith('s');
    });
});
