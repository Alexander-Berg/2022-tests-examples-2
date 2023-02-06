import * as path from 'path';
import * as fs from 'fs';
import { IDivData, ITemplates } from 'divcard2';
import { buildDivcard } from '../index';
import * as apiSearchV2 from './mocks/api-search-2.json';
import * as _req from './mocks/req.json';
import * as zenExport from './mocks/zen-export.json';
import * as zenConfig from './mocks/zen-config.json';
import { buildAlert } from '../alerts';
import { testShortcutsHandle } from '../alerts/geoblock2/test-handle';
import { TestConfig } from './data';
import { BlockDataBase } from '../cards/handler';

import { forceDarkColors } from '../common/base-app-req';

type TestBlockData = IDivData & { ttl: string; ttv: string } &
    { data: IDivData; corner_radius: number; no_menu: number};

export function buildCardResponse({
    id,
    type = 'card',
    isDark,
    cards
}: {
    id: string;
    type?: 'card' | 'alert' | 'shortcut' | 'shortcut-wide';
    isDark?: boolean;
    cards?: string;
}) {
    const req = isDark ? forceDarkColors(_req) : _req;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (req as any).is_redesign = 1;

    let data;
    let cardsObj;

    if (!cards) {
        data = getData(id, type);
    } else {
        cardsObj = JSON.parse(cards);
    }

    let result: {
        templates: ITemplates;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        card: any;
    };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const res: any = Object.assign({}, apiSearchV2);
    const zen_extensions = [];

    if (type?.startsWith('shortcut')) {
        const cardData = {
            type: 'geoblock',
            id: 'informers',
            subs_data: {
                topic: 'informers_card'
            },
            data: {
                geoblock_alert_source: 'hermione',
                shortcuts: data
            }
        };
        result = testShortcutsHandle(
            {
                ...req,
                logger: console,
                Getargshash: {
                    dp: '2'
                },
                userDevice: {
                    app_platform: 'android',
                    dpi: 2,
                    screenx: type === 'shortcut-wide' ? 720 : 1200,
                    screeny: 1920,
                    uuid: '123'
                },
                is_geoblock: '1'
            },
            cardData
        );

        zen_extensions.push(
            {
                heavy: 0,
                id: 'informers',
                position: 0,
                type: 'div2',
                zen_id: 'placeholder_0'
            },
            {
                heavy: 0,
                id: id + '_empty',
                position: 1,
                type: 'div2',
                zen_id: 'placeholder_1'
            }
        );
    } else if (cards) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        let block: any = [];
        const templates = {};
        let position = 0;

        for (let { id, name } of cardsObj) {
            const data = getData(name, type);
            const isAlert = type === 'alert';
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const result = isAlert ? buildAlert(data as any, req as any) :
                buildDivcard(id, data as BlockDataBase, { ...req, id, logger: console });

            block = block.concat(makeBlock(name, result.card as TestBlockData));

            zen_extensions.push(
                {
                    heavy: 0,
                    id: name,
                    position,
                    type: 'div2',
                    zen_id: 'placeholder_' + position
                },
                {
                    heavy: 0,
                    id: name + '_empty',
                    position: position + 1,
                    type: 'div2',
                    zen_id: 'placeholder_' + (position + 1)
                }
            );
            Object.assign(templates, result.templates);
            position += 2;
        }
        res.block = block;

        res.div_templates = templates;

        res.extension_block = {
            zen_extensions
        };

        return res;
    } else {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        result = type === 'alert' ? buildAlert(data as any, req as any) :
            buildDivcard(id, data as BlockDataBase, { ...req, id, logger: console });

        zen_extensions.push(
            {
                heavy: 0,
                id,
                position: 0,
                type: 'div2',
                zen_id: 'placeholder_0'
            },
            {
                heavy: 0,
                id: id + '_empty',
                position: 1,
                type: 'div2',
                zen_id: 'placeholder_1'
            }
        );
    }

    const { templates, card } = result;

    res.extension_block = {
        zen_extensions
    };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    res.block = makeBlock(id, card);
    res.div_templates = templates;

    res.extension_block = {
        zen_extensions: [
            {
                heavy: 0,
                id,
                position: 1,
                type: 'div2',
                zen_id: 'placeholder_0'
            }
        ]
    };

    return res;
}

export function mockZenExport() {
    let items = [];

    for (let i = 0; i < 200; i++) {
        items.push({
            id: String(i),
            type: 'card',
            pos: i,
            card_type: 'placeholder',
            card_payload: 'placeholder_' + i,
            heartbeat_pos: []
        });
    }

    return Object.assign({}, zenExport, { items });
}

export function mockZenConfig() {
    return zenConfig;
}

function mockPath(id: string, type: 'card' | 'alert' | 'shortcut' | 'shortcut-wide') {
    const suffixPath = `${type === 'shortcut-wide' ? 'shortcut' : type}s`;
    return path.join(__dirname, `mocks/${suffixPath}-data`, `${id}.data.json`);
}

export function generateTestData(id: string, data: unknown, type: 'card' | 'alert' | 'shortcut' | 'shortcut-wide' = 'card', config?: TestConfig) {
    // старый вариант
    const dataPath = mockPath(id, type);

    if (!config && !fs.existsSync(dataPath)) {
        return fs.writeFileSync(dataPath, JSON.stringify(data, null, '  '));
    }

    if (!(config && config.cases)) {
        return;
    }

    const { cases } = config;

    cases.forEach(test => {
        const fileName = `${id}#${test.name}`;
        const dataPath = mockPath(fileName, type);
        if (test.condition(data) && !fs.existsSync(dataPath)) {
            fs.writeFileSync(dataPath, JSON.stringify(data, null, '  '));
        }
    });
}

function getData(id: string, type: 'card' | 'alert' | 'shortcut' | 'shortcut-wide'): unknown {
    const dataPath = mockPath(id, type);

    if (!fs.existsSync(dataPath)) {
        throw new Error(`${id} (${type}): missing mock data! Add data manually.`);
    }

    return JSON.parse(fs.readFileSync(dataPath, { encoding: 'utf-8' }));
}

function makeBlock(id: string, card: TestBlockData) {
    return [
        {
            id,
            data: {
                states: card.data?.states || card.states,
                log_id: id
            },
            no_menu: card.no_menu,
            corner_radius: card.corner_radius,
            type: 'div2',
            topic: `${id}_card`,
            ttl: 900,
            ttv: 1200,
            utime: Date.now(),
        },
        // пустой невидимы блок, чтобы на одном скрине не было больше одного блока
        {
            id: id + '_empty',
            data: {
                log_id: id,
                states: [{
                    state_id: 1,
                    div: {
                        type: 'container',
                        items: [
                            {
                                width: {
                                    type: 'fixed',
                                    value: 0
                                },
                                delimiter_style: {
                                    orientation: 'vertical',
                                    color: '#00000000'
                                },
                                height: {
                                    value: 800,
                                    type: 'fixed'
                                },
                                type: 'separator'
                            }
                        ],
                        width: {
                            type: 'fixed',
                            value: 100
                        }
                    }
                }
                ]
            },
            type: 'div2',
            topic: id + 'empty_card',
            ttl: 900,
            ttv: 1200,
            utime: Date.now()
        }
    ];
}
