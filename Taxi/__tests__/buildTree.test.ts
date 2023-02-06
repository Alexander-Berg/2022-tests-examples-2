import {SettingItem, SettingsTree, SettingsTreeItem} from '../types';
import {buildTree} from '../utils';

function getSetting(path: string[], item: SettingsTreeItem | SettingsTree): SettingsTreeItem | undefined {
    if (path.length === 0) {
        return item as SettingsTreeItem;
    }
    return getSetting(
        path.slice(1),
        item.children?.find((child: SettingsTreeItem) => child.key === path[0]) as SettingsTreeItem
    );
}

describe('buildTree', () => {
    test('Корректно строит дерево', () => {
        const flat: SettingItem[] = [
            {
                setting_key: 'a.b.c.d',
                setting_value: 'this is a.b.c.d'
            },
            {
                setting_key: 'a',
                setting_value: 'this is a'
            }
        ];

        const tree = buildTree(flat);
        const expected = {
            children: [
                {
                    key: 'a',
                    path: 'a',
                    value: 'this is a',
                    children: [
                        {
                            key: 'b',
                            path: 'a.b',
                            children: [
                                {
                                    key: 'c',
                                    path: 'a.b.c',
                                    children: [
                                        {
                                            key: 'd',
                                            path: 'a.b.c.d',
                                            value: 'this is a.b.c.d'
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        };

        expect(tree).toEqual(expected);
    });
    test('Все значения из списка настроек доступны в дереве настроек', () => {
        const flat: SettingItem[] = [
            {
                setting_key: 'a',
                setting_value: 'testroot'
            },
            {
                setting_key: 'a.b.c.d',
                setting_value: '123'
            },
            {
                setting_key: 'e.f.g.h.k.l',
                setting_value: 'lesp'
            },
            {
                setting_key: 'e.m',
                setting_value: 'test'
            },
            {
                setting_key: 'a.b',
                setting_value: 'test'
            },
            {
                setting_key: 'e',
                setting_value: 'hello'
            }
        ];

        const tree = buildTree(flat);

        for (const setting of flat) {
            const {value, path} = getSetting(setting.setting_key.split('.'), tree) || {};
            expect(value).toBe(setting.setting_value);
            expect(path).toBe(setting.setting_key);
        }
    });

    test('Вернет дерево с пустым children в случае пустого массива', () => {
        const flat: SettingItem[] = [];

        const tree = buildTree(flat);
        const expected: SettingsTree = {
            children: []
        };

        expect(tree).toEqual(expected);
    });
});
