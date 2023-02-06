import * as React from 'react';

import { renderHook, act, RenderResult } from '@testing-library/react-hooks';
import { useCheckboxState } from '../use-checkbox-state';

const items = [
    {
        id: 1,
        label: 'Checkbox1',
    },
    {
        id: 2,
        label: 'Checkbox3',
    },
];

function renderStateHook(): RenderResult<ReturnType<typeof useCheckboxState>> {
    const { result } = renderHook(() => useCheckboxState(items));
    return result;
}

function emulateChangeEvent(result: RenderResult<ReturnType<typeof useCheckboxState>>, index = 0): void {
    act(() => {
        const { itemsPropSets } = result.current;
        itemsPropSets[index].onChange({} as React.ChangeEvent);
    });
}

describe('Checkbox', () => {
    describe('use-checkbox-state', () => {
        it('should add checked value', () => {
            const result = renderStateHook();

            emulateChangeEvent(result);

            const { selectedIds } = result.current;
            expect(selectedIds).toContain(items[0].id);
            expect(selectedIds).not.toContain(items[1].id);
        });

        it('should remove checked value', () => {
            const result = renderStateHook();

            emulateChangeEvent(result);
            emulateChangeEvent(result);

            const { selectedIds } = result.current;
            expect(selectedIds).not.toContain(items[0].id);
        });
    });
});
