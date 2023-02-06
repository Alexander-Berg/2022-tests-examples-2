import * as React from 'react';

import { renderHook, act, RenderResult } from '@testing-library/react-hooks';
import { useRadioState } from '../use-radio-state';

const items = [
    {
        id: 1,
        label: 'Radio1',
    },
    {
        id: 2,
        label: 'Radio2',
    },
];

function renderStateHook(): RenderResult<ReturnType<typeof useRadioState>> {
    const { result } = renderHook(() => useRadioState(items));
    return result;
}

function emulateChangeEvent(result: RenderResult<ReturnType<typeof useRadioState>>, index = 0): void {
    act(() => {
        const { itemsPropSets } = result.current;
        itemsPropSets[index].onChange({} as React.ChangeEvent);
    });
}

describe('Checkbox', () => {
    describe('use-radio-state', () => {
        it('should check value', () => {
            const result = renderStateHook();

            emulateChangeEvent(result);

            const { selectedId } = result.current;
            expect(selectedId).toEqual(items[0].id);
        });

        it('should check other value', () => {
            const result = renderStateHook();

            emulateChangeEvent(result, 0);
            emulateChangeEvent(result, 1);

            const { selectedId } = result.current;
            expect(selectedId).toEqual(items[1].id);
        });

        it('shouldn"t uncheck checked value', () => {
            const result = renderStateHook();

            emulateChangeEvent(result, 0);
            emulateChangeEvent(result, 0);

            const { selectedId } = result.current;
            expect(selectedId).toEqual(items[0].id);
        });
    });
});
