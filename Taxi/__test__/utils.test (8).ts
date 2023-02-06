import {expectSaga} from 'redux-saga-test-plan';
import {call} from 'redux-saga/effects';

import {AdminGeoNode} from '_api/geo-hierarchy/types';
import {apiInstance as tariffsApiInstance} from '_api/tariffs/TariffsAPI';

import {CorrectedGoalRule, CorrectedSingleRideRule, TariffSettingsZone} from '../../../types';
import {GEONODES_OPERATION} from '../consts';
import SmartSubventionService from '../SmartSubventionService';
import {getTimezonesData} from '../utils';

describe('getTimezonesData', () => {
    it('должна хранить данные по таймзонам в нужном формате', () => {
        const rules: Array<CorrectedSingleRideRule | CorrectedGoalRule> = [
            {
                id: '00e74a31-5caf-450d-b8cb-327426081db8',
                start: '2021-03-10T19:00:00+00:00',
                end: '2022-03-09T19:00:00+00:00',
                updated_at: '2021-03-10T18:56:29.757587+00:00',
                activity_points: 47,
                rates: [],
                budget_id: '232a04eb-96bc-43ec-b6e6-0c33da308446',
                schedule_ref: '139930',
                draft_id: '139930',
                zone: 'moscow',
                tariff_class: 'business',
                geoarea: 'msk_iter7_pol31',
                rule_type: 'single_ride',
            },
            {
                id: '0cec0839-c820-4fbb-9fc8-ba6bcd58dbbc',
                start: '2021-03-10T19:00:00+00:00',
                end: '2022-03-09T19:00:00+00:00',
                updated_at: '2021-03-10T18:56:29.757587+00:00',
                activity_points: 47,
                rates: [],
                budget_id: '232a04eb-96bc-43ec-b6e6-0c33da308446',
                schedule_ref: '139930',
                draft_id: '139930',
                zone: 'moscow',
                tariff_class: 'uberx',
                geoarea: 'msk_iter7_pol21',
                rule_type: 'single_ride',
            },
            {
                id: '12c8c9c4-e74b-4578-8556-3b6a3c4e4b5f',
                tariff_class: 'econom',
                geonode:
                    'br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_near_region/br_reutov',
                counters: {
                    schedule: [],
                    steps: [],
                },
                global_counters: [{local: 'A', global: '160469:A'}],
                window: 3,
                currency: 'RUB',
                start: '2021-04-27T21:00:00+00:00',
                end: '2021-05-24T21:00:00+00:00',
                updated_at: '2021-04-27T09:42:22.677633+00:00',
                budget_id: '5fff9b70-5872-421f-b828-fe26d1400f35',
                draft_id: '160469',
                branding_type: 'no_full_branding',
                activity_points: 80,
                geoarea: 'tst_pol6',
                rule_type: 'goal',
                schedule_ref: 'schedule_ref',
            },
            {
                id: '25d827bc-d456-40a9-82e7-0891c1abfcce',
                tariff_class: 'uberx',
                geonode:
                    'br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_near_region/br_reutov',
                counters: {
                    schedule: [],
                    steps: [],
                },
                global_counters: [{local: 'A', global: '160469:A'}],
                window: 3,
                currency: 'RUB',
                start: '2021-04-27T21:00:00+00:00',
                end: '2021-05-24T21:00:00+00:00',
                updated_at: '2021-04-27T09:42:22.677633+00:00',
                budget_id: '5fff9b70-5872-421f-b828-fe26d1400f35',
                draft_id: '160469',
                branding_type: 'no_full_branding',
                activity_points: 80,
                geoarea: 'tst_pol6',
                rule_type: 'goal',
                schedule_ref: 'schedule_ref',
            },
            {
                id: '3a764230-38c9-4393-8869-4c11256e76da',
                tariff_class: 'uberx',
                geonode: 'br_root/br_russia/br_privolzhskij_fo/br_samarskaja_obl/br_samara/br_samara_adm',
                counters: {
                    schedule: [],
                    steps: [],
                },
                global_counters: [{local: 'A', global: '159315:A'}],
                window: 2,
                currency: 'RUB',
                start: '2021-04-23T20:00:00+00:00',
                end: '2021-05-27T20:00:00+00:00',
                updated_at: '2021-04-23T15:19:44.003021+00:00',
                budget_id: '8ecae3ba-7884-4335-878a-dcab86e5688e',
                draft_id: '159315',
                activity_points: 55,
                rule_type: 'goal',
                schedule_ref: 'schedule_ref',
            },
            {
                id: '73ae933d-065a-49ea-9d78-03ffa3de24ab',
                tariff_class: 'econom',
                geonode: 'br_root/br_russia/br_privolzhskij_fo/br_samarskaja_obl/br_samara/br_samara_adm',
                counters: {
                    schedule: [],
                    steps: [],
                },
                global_counters: [{local: 'A', global: '159315:A'}],
                window: 2,
                currency: 'RUB',
                start: '2021-04-23T20:00:00+00:00',
                end: '2021-05-27T20:00:00+00:00',
                updated_at: '2021-04-23T15:19:44.003021+00:00',
                budget_id: '8ecae3ba-7884-4335-878a-dcab86e5688e',
                draft_id: '159315',
                activity_points: 55,
                rule_type: 'goal',
                schedule_ref: 'schedule_ref',
            },
        ];
        const geoNodes: Array<AdminGeoNode> = [
            {
                name: 'br_reutov',
                hierarchy_type: 'BR',
                node_type: 'node',
                name_ru: 'Реутов',
                name_en: 'Reutov',
                tariff_zones: ['reutov'],
                parents: ['br_moscow_near_region'],
                population: 103779,
                oebs_mvp_id: 'MSKc',
                region_id: '21621',
                regional_managers: ['milabelova'],
                operational_managers: ['susloparov'],
            },
            {
                name: 'br_samara_adm',
                hierarchy_type: 'BR',
                node_type: 'node',
                name_ru: 'Самара (адм)',
                name_en: 'Samara (adm)',
                tariff_zones: ['samara'],
                parents: ['br_samara'],
                population: 1169719,
                oebs_mvp_id: 'SAMc',
                region_id: '51',
                regional_managers: ['kotbegemot'],
                operational_managers: ['aglukhov'],
            },
        ];
        const TIMEZONE_SETTINGS: Array<TariffSettingsZone> = [
            {
                zone: 'moscow',
                tariff_settings: {
                    city_id: 'Москва',
                    classifier_name: 'Москва',
                    timezone: 'Europe/Moscow',
                },
            },
            {
                zone: 'reutov',
                tariff_settings: {
                    city_id: 'Москва',
                    classifier_name: 'Москва',
                    timezone: 'Europe/Moscow',
                },
            },
            {
                zone: 'samara',
                tariff_settings: {
                    city_id: 'Самара',
                    timezone: 'Europe/Samara',
                },
            },
        ];
        return expectSaga(getTimezonesData, rules)
            .withState({
                asyncOperations: {
                    [GEONODES_OPERATION]: geoNodes,
                },
            })
            .provide([
                [call(SmartSubventionService.requestGeoNodes), geoNodes],
                [call(tariffsApiInstance.getTariffSettings, 'moscow,reutov,samara'), TIMEZONE_SETTINGS],
            ])
            .run()
            .then(resp => {
                const expectedResult = [
                    {
                        zone: 'moscow',
                        tariffZone: 'moscow',
                        timeZoneData: {
                            name: 'Europe/Moscow',
                            offsetData: 'Europe/Moscow smart_subventions.msk0',
                            offset: 0,
                            correctedOffset: 3,
                            currency: 'RUB',
                        },
                    },
                    {
                        zone: 'br_reutov',
                        tariffZone: 'reutov',
                        timeZoneData: {
                            name: 'Europe/Moscow',
                            offsetData: 'Europe/Moscow smart_subventions.msk0',
                            offset: 0,
                            correctedOffset: 3,
                            currency: 'RUB',
                        },
                    },
                    {
                        zone: 'br_samara_adm',
                        tariffZone: 'samara',
                        timeZoneData: {
                            name: 'Europe/Samara',
                            offsetData: 'Europe/Samara smart_subventions.msk+1',
                            offset: 1,
                            correctedOffset: 4,
                            currency: 'RUB',
                        },
                    },
                ];
                expect(resp.returnValue).toEqual(expectedResult);
            });
    });
});
