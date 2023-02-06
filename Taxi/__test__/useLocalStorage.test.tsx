import {screen, fireEvent, render} from '@testing-library/react';
import React from 'react';

import {createStoreProvider} from 'utils/tests/renders';

import Component from './component';

describe('useLocalStorage tests', () => {
    test('useLocalStorage should return initial value', async () => {
        render(createStoreProvider(<Component/>));

        // Проверяем начальное состояние компонента
        expect(screen.getByText(/initial/)).toBeDefined();
    });

    test('useLocalStorage should correctly update value', async () => {
        render(createStoreProvider(<Component/>));

        fireEvent.click(screen.getByRole('button', {name: /Change value/i}));
        // Ждём, что хук отработает и значение обновится
        expect(await screen.findByText(/test/)).toBeDefined();
        expect(screen.queryByText(/initial/)).toBeNull();
    });
});
