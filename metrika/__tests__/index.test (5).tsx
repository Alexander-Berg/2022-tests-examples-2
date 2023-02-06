import * as React from 'react';
import { Size } from 'typings';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotRenderTest } from 'testing/jest-utils';
import { FormRow, FormRowDirection } from '..';

// Спискок всех возможных значений свойства 'direction'
const directions: Array<FormRowDirection> = ['vertical', 'horizontal'];

/**
 * Список React компонентов со всеми возможными значениями свойства 'direction'
 * Список генерируется автоматически на основании доступных значений свойств
 */
const allPossibleDirections: ReactElementsList = directions.reduce(
    (list, direction) => ({
        ...list,
        [`with direction="${direction}" prop`]: (
            <FormRow size={Size.S} direction={direction} />
        ),
    }),
    {},
);

/**
 * Список React компонентов для базовых случаев
 * Генерируется вручную
 */
const simpleCases: ReactElementsList = {
    'with default props': <FormRow size={Size.S} />,
    'with className': <FormRow size={Size.S} className="className" />,

    'with label': (
        <FormRow size={Size.S}>
            <FormRow.Label>label</FormRow.Label>
        </FormRow>
    ),

    'with label and passed labelWidth prop': (
        <FormRow size={Size.S}>
            <FormRow.Label labelWidth="130px">label</FormRow.Label>
        </FormRow>
    ),

    'with label and passed mixes and mods': (
        <FormRow size={Size.S}>
            <FormRow.Label
                labelWidth="130px"
                mix={{ block: 'block' }}
                mods={{ mod: true }}
            >
                label
            </FormRow.Label>
        </FormRow>
    ),

    'with label and passed className to it': (
        <FormRow size={Size.S}>
            <FormRow.Label className="className">label</FormRow.Label>
        </FormRow>
    ),

    'with control': (
        <FormRow size={Size.S}>
            <FormRow.Control>control</FormRow.Control>
        </FormRow>
    ),

    'with control and passed controlWidth prop': (
        <FormRow size={Size.S}>
            <FormRow.Control controlWidth="130px">control</FormRow.Control>
        </FormRow>
    ),

    'with control and passed mixes and mods': (
        <FormRow size={Size.S}>
            <FormRow.Control
                controlWidth="130px"
                mods={{ mod: true }}
                mix={{ block: 'block' }}
            >
                control
            </FormRow.Control>
        </FormRow>
    ),

    'with control and passed className to it': (
        <FormRow size={Size.S}>
            <FormRow.Control className="className">control</FormRow.Control>
        </FormRow>
    ),

    'with list': (
        <FormRow size={Size.S}>
            <FormRow.List>
                {'item1'}
                {'item2'}
                {'item3'}
            </FormRow.List>
        </FormRow>
    ),

    'with list and passed mixes and mods': (
        <FormRow size={Size.S}>
            <FormRow.List mods={{ mod: true }} mix={{ block: 'block' }}>
                {'item1'}
                {'item2'}
                {'item3'}
            </FormRow.List>
        </FormRow>
    ),

    'with list and passed className': (
        <FormRow size={Size.S}>
            <FormRow.List className="className">раз</FormRow.List>
        </FormRow>
    ),
};

// Объединение всех объявленных выше списков
// ВАЖНО: Все элементы из списка тестируются используя метод render библиотеки enzyme !!!
// Для использования shallow и пр. необходимо использовать отдельный список
const componentsForSnapshotRenderTest: ReactElementsList = {
    ...simpleCases,
    ...allPossibleDirections,
};

describe('FormRow', () => {
    describe('renders', () => {
        jestSnapshotRenderTest(componentsForSnapshotRenderTest);
    });
});
