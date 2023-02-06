import {
    Block,
    ContainerBlock,
    GalleryBlock,
    NonEmptyArray,
    SolidBackground
} from 'divcard2';
import { createHandler } from '../alert-handle';
import { partition } from '../../utils';
import { Colors } from '../../common/colors';
import { colorScheme, GeoblockColorScheme } from './colors';
import { handleShortcut } from './shortcuts';
import { templates } from './templates';
import { Data } from './data';

/** Хэндлер для снятия скриншотов шорткатов в hermione-тестах */
export const testShortcutsHandle = createHandler({
    templates,
    colorScheme,
    handle(data: Data, colors: Colors<GeoblockColorScheme>) {
        const items = partition(
            data.shortcuts.map((shortcut, idx) =>
                handleShortcut.call(this, shortcut, idx)),
            3).map(row =>
            new GalleryBlock({
                item_spacing: 8,
                paddings: { bottom: 8 },
                items: row as Block[]
            }));

        return {
            states: [
                {
                    state_id: 1,
                    div: new ContainerBlock({
                        background: [new SolidBackground({
                            color: colors.portal.background.primary
                        })],
                        items: items as NonEmptyArray<Block>
                    })
                }
            ]
        };
    }
});
