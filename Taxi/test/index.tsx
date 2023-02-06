import React from 'react';
import type { XXX } from './type';

export type { XXX } from './type';

const CONST = (...[part2]: [part2: string]) => {
    const part1 = 'часть 1';
    return `Текст из двух частей: ${part1}, ${part2}`;
}

const TestComponent: React.FC<{}> = () => (
    <div data-text="Текст в атрибуте">
        Тестовый текст очень интересный
        {CONST('Часть 2')}
    </div>
)

export default TestComponent;