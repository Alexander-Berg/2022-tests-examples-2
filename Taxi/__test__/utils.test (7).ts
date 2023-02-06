import {AdminGeoNode} from '_api/geo-hierarchy/types';
import {getCurrency} from '_pkg/utils/getCurrency';

describe('getCurrency', () => {
    it('Должна возвращать валюту страны, если есть геонода с ней', () => {
        const geoNodes: Array<AdminGeoNode> = [
            {
                hierarchy_type: 'BR',
                name: 'br_accra',
                name_en: 'Accra',
                name_ru: 'Аккра',
                node_type: 'agglomeration',
                oebs_mvp_id: 'ACCr',
                parents: ['fi_gh_1mp', 'br_ghana', 'op_ghana'],
                population: 2270000,
                region_id: '20803',
                tariff_zones: ['accra'],
            },
            {
                children: ['br_accra', 'br_kumasi', 'br_tamale'],
                currency: 'GHS',
                hierarchy_type: 'BR',
                name: 'br_ghana',
                name_en: 'Ghana',
                name_ru: 'Гана',
                node_type: 'country',
                parents: ['br_root'],
                region_id: '20802',
            },
        ];
        const currency = getCurrency(geoNodes, 'br_accra');

        expect(currency).toEqual('GHS');
    });

    it('Должна возвращать дефолтное значение, если валюта не найдена в геонодах', () => {
        const geoNodes: Array<AdminGeoNode> = [
            {
                hierarchy_type: 'BR',
                name: 'br_accra',
                name_en: 'Accra',
                name_ru: 'Аккра',
                node_type: 'agglomeration',
                oebs_mvp_id: 'ACCr',
                parents: ['fi_gh_1mp', 'br_ghana', 'op_ghana'],
                population: 2270000,
                region_id: '20803',
                tariff_zones: ['accra'],
            },
            {
                children: ['br_accra', 'br_kumasi', 'br_tamale'],
                hierarchy_type: 'BR',
                name: 'br_ghana',
                name_en: 'Ghana',
                name_ru: 'Гана',
                node_type: 'country',
                parents: ['br_root'],
                region_id: '20802',
            },
        ];
        const currency = getCurrency(geoNodes, 'br_accra');

        expect(currency).toEqual('RUB');
    });

    it('Должна возвращать нужную валюту, если передана тарифная зона, а не имя геоноды', () => {
        const geoNodes: Array<AdminGeoNode> = [
            {
                hierarchy_type: 'BR',
                name: 'br_accra',
                name_en: 'Accra',
                name_ru: 'Аккра',
                node_type: 'agglomeration',
                oebs_mvp_id: 'ACCr',
                parents: ['fi_gh_1mp', 'br_ghana', 'op_ghana'],
                population: 2270000,
                region_id: '20803',
                tariff_zones: ['accra'],
            },
            {
                children: ['br_accra', 'br_kumasi', 'br_tamale'],
                hierarchy_type: 'BR',
                name: 'br_ghana',
                name_en: 'Ghana',
                name_ru: 'Гана',
                node_type: 'country',
                parents: ['br_root'],
                region_id: '20802',
            },
        ];
        const currency = getCurrency(geoNodes, 'accra');

        expect(currency).toEqual('RUB');
    });
});
