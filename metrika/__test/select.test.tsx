import React, { FC } from 'react';

import { TestContext } from '@client-libs/mindstorms/service/test-context/test-context';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';

import userEvent from '@testing-library/user-event';
import { render, screen } from '@testing-library/react';
import { SelectProps } from '../select-props';
import { Select } from '../select';

const items = [
    { title: 'Все тесты', id: 'ALL' },
    { title: 'Черновики', id: 'DRAFT' },
    { title: 'Запланированные', id: 'QUEUED' },
    { title: 'Запущенные', id: 'RUNNING' },
    { title: 'Остановленные', id: 'STOPPED' },
    { title: 'Закрытые', id: 'CLOSED' },
];

const SelectComponent: FC<Partial<SelectProps>> = ({ onSelect, selectedIds, ...props }) => {
    const [ids, setIds] = React.useState<string[]>(selectedIds ?? []);

    const handleSelect = React.useCallback(
        (values: string[]) => {
            setIds(values);

            if (onSelect) {
                onSelect(values);
            }
        },
        [onSelect]
    );

    return <Select items={items} selectedIds={ids} onSelect={handleSelect} {...props} />;
};

const SelectExample: FC<Partial<SelectProps>> = props => (
    <TestContext.Provider value={true}>
        <SelectComponent {...props} />
    </TestContext.Provider>
);

describe('Select', () => {
    describe('screenshot', () => {
        it('default', async () => {
            await makeScreenshot(<SelectExample selectedIds={['ALL']} />, { width: 300, height: 300 });
        });

        it('disabled', async () => {
            await makeScreenshot(<SelectExample isDisabled selectedIds={['DRAFT']} />, { width: 300, height: 300 });
        });

        it('multiple', async () => {
            await makeScreenshot(<SelectExample isMultiple selectedIds={['ALL', 'DRAFT', 'CLOSED']} />, {
                width: 300,
                height: 300,
            });
        });
    });

    describe('logic', () => {
        const onSelect = jest.fn();

        const renderSelect = (props?: Partial<SelectProps>): void => {
            render(<SelectComponent onSelect={onSelect} {...props} />);
        };

        const openSelect = (): void => {
            const button = document.querySelector('button')!;
            userEvent.click(button);
        };

        const selectItem = (index: number): string => {
            const { title, id } = items[index];
            userEvent.click(screen.getByText(title));
            return id;
        };

        beforeEach(() => {
            onSelect.mockClear();
        });

        it('should select item', () => {
            renderSelect();
            openSelect();

            const id = selectItem(2);

            expect(onSelect).toBeCalledWith([id]);
        });

        it('should select multiple items', () => {
            renderSelect({ isMultiple: true });
            openSelect();

            const id1 = selectItem(1);
            const id2 = selectItem(2);
            const id3 = selectItem(3);

            expect(onSelect.mock.calls).toEqual([[[id1]], [[id2, id1]], [[id3, id2, id1]]]);
        });

        it('should disable deselect the only one item', () => {
            renderSelect();

            openSelect();
            userEvent.click(screen.getAllByText(items[2].title)[0]);

            openSelect();
            userEvent.click(screen.getAllByText(items[2].title)[1]);

            expect(onSelect.mock.calls).toEqual([[[items[2].id]]]);
        });

        it('should allow deselect the only one item by flag', () => {
            renderSelect({ isEmptyEnabled: true });

            openSelect();
            userEvent.click(screen.getAllByText(items[2].title)[0]);

            openSelect();
            userEvent.click(screen.getAllByText(items[2].title)[1]);

            expect(onSelect.mock.calls).toEqual([[[items[2].id]], [[]]]);
        });
    });
});
