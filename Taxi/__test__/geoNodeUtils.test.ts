import {AdminGeoNode} from '_api/geo-hierarchy/types';

import {filterGeoNodes, getFinalGeonodeName} from '../utils';

describe('getFinalGeonodeName', () => {
    it('должна возвращать строку заданного формата', () => {
        const geoNodes: Array<AdminGeoNode> = [
            {
                name: 'br_moscow',
                hierarchy_type: 'BR',
                node_type: 'agglomeration',
                children: ['br_moscow_adm'],
                name_ru: 'Москва',
                name_en: 'Moscow',
                oebs_mvp_id: 'MSKc',
                region_id: '213',
                operational_managers: ['susloparov'],
            },
            {
                name: 'br_moskovskaja_obl',
                hierarchy_type: 'BR',
                node_type: 'node',
                children: ['br_moscow'],
                name_ru: 'Московская область',
                name_en: 'Moscow Region',
                tags: ['region'],
            },
            {
                name: 'br_tsentralnyj_fo',
                hierarchy_type: 'BR',
                node_type: 'node',
                children: ['br_moskovskaja_obl'],
                name_ru: 'Центральный ФО',
                name_en: 'Central Federal District',
                tags: ['federal district'],
                region_id: '3',
            },
            {
                name: 'br_russia',
                hierarchy_type: 'BR',
                node_type: 'country',
                children: ['br_tsentralnyj_fo'],
                name_ru: 'Россия',
                name_en: 'Russia',
                operational_managers: ['berenda'],
            },
            {
                name: 'br_root',
                hierarchy_type: 'BR',
                node_type: 'root',
                children: ['br_russia'],
                name_ru: 'Базовая иерархия',
                name_en: 'Basic Hierarchy',
                tags: ['prosoteg'],
                sort_priority: 325,
                parent_priority: 41,
                oebs_mvp_id: 'MMMVVVPP',
                region_id: '7',
                regional_managers: ['nenatalich'],
                operational_managers: ['nenatalich'],
            },
        ];
        const result = getFinalGeonodeName(geoNodes, 'br_moscow_adm');
        const expectedResult = 'br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm';

        expect(result).toEqual(expectedResult);
    });
});

describe('filterGeoNodes', () => {
    it('должна фильтровать геоноды без тарифных зон', () => {
        const geoNodes: Array<AdminGeoNode> = [
            {
                name: 'br_moscow',
                hierarchy_type: 'BR',
                node_type: 'agglomeration',
                children: ['br_moscow_adm'],
                tariff_zones: ['tariff_zone_1'],
                name_ru: 'Москва',
                name_en: 'Moscow',
                oebs_mvp_id: 'MSKc',
                region_id: '213',
                operational_managers: ['susloparov'],
            },
            {
                name: 'br_moscow',
                hierarchy_type: 'BR',
                node_type: 'agglomeration',
                tariff_zones: ['tariff_zone_1', 'tariff_zone_2'],
                name_ru: 'Москва',
                name_en: 'Moscow',
                oebs_mvp_id: 'MSKc',
                region_id: '213',
                operational_managers: ['susloparov'],
            },
            {
                name: 'br_moscow',
                hierarchy_type: 'BR',
                node_type: 'agglomeration',
                children: ['br_moscow_adm'],
                name_ru: 'Москва',
                name_en: 'Moscow',
                oebs_mvp_id: 'MSKc',
                region_id: '213',
                operational_managers: ['susloparov'],
            },
        ];
        const expectedResult: Array<AdminGeoNode> = [
            {
                name: 'br_moscow',
                hierarchy_type: 'BR',
                node_type: 'agglomeration',
                children: ['br_moscow_adm'],
                tariff_zones: ['tariff_zone_1'],
                name_ru: 'Москва',
                name_en: 'Moscow',
                oebs_mvp_id: 'MSKc',
                region_id: '213',
                operational_managers: ['susloparov'],
            },
            {
                name: 'br_moscow',
                hierarchy_type: 'BR',
                node_type: 'agglomeration',
                tariff_zones: ['tariff_zone_1', 'tariff_zone_2'],
                name_ru: 'Москва',
                name_en: 'Moscow',
                oebs_mvp_id: 'MSKc',
                region_id: '213',
                operational_managers: ['susloparov'],
            },
        ];

        expect(filterGeoNodes(geoNodes)).toEqual(expectedResult);
    });
});
