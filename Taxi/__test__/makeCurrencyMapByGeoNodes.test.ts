import {AdminGeoNode} from '_api/geo-hierarchy/types';

import {makeCurrencyMapByGeoNodes} from '../makeCurrencyMapByGeoNodes';

const NODE_NAME = {
    ROOT: 'root',
    RUSSIA: 'russia',
    MOSCOW: 'moscow',
    BR_MOSCOW: 'br_moscow',
    NOVGOROD: 'novgorod',
};

const NODE_TYPE = {
    COUNTRY: 'country',
    ROOT: 'root',
    NODE: 'node',
    AGGLOMERATION: 'agglomeration'
} as const;

const BR = 'BR';
const RUB = 'RUB';
const EUR = 'EUR';

const GEO_NODES: AdminGeoNode[] = [
    {
        name: NODE_NAME.RUSSIA,
        hierarchy_type: BR,
        node_type: NODE_TYPE.COUNTRY,
        children: [NODE_NAME.BR_MOSCOW, NODE_NAME.NOVGOROD],
        name_ru: '',
        name_en: '',
    },
    {
        name: NODE_NAME.ROOT,
        hierarchy_type: BR,
        node_type: NODE_TYPE.ROOT,
        currency: EUR,
        children: [NODE_NAME.RUSSIA],
        name_ru: '',
        name_en: '',
    },
    {
        name: NODE_NAME.BR_MOSCOW,
        hierarchy_type: BR,
        currency: RUB,
        node_type: NODE_TYPE.AGGLOMERATION,
        tariff_zones: [NODE_NAME.MOSCOW],
        name_ru: '',
        name_en: '',
    },
    {
        name: NODE_NAME.NOVGOROD,
        hierarchy_type: BR,
        node_type: NODE_TYPE.NODE,
        name_ru: '',
        name_en: '',
    },
];

describe('makeCurrencyMapByGeoNodes', () => {
    const result = makeCurrencyMapByGeoNodes(GEO_NODES);
    it('Формирование коллекции валют по нодам', () => {
        expect(result).toEqual({
            [NODE_NAME.ROOT]: EUR,
            [NODE_NAME.NOVGOROD]: EUR,
            [NODE_NAME.BR_MOSCOW]: RUB,
            [NODE_NAME.MOSCOW]: RUB,
            [NODE_NAME.RUSSIA]: EUR,
        });
    });
});
