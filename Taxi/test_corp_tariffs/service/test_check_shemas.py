import generated.models.individual_tariffs.tariff as individual_tariffs

import corp_tariffs.generated.service.swagger.models.api as corp_tariffs
import corp_tariffs.utils.name_mapping as mapping


async def test_check_schemas(load_json):
    # тариф в этом файле целиком соответсвует текущей схеме
    # individual_tariffs.tariff
    tariff = individual_tariffs.Tariff.deserialize(
        load_json('full_individual_tariffs_tariff.json'),
    )
    tariff = tariff.serialize()
    # кастим представлению тарифа в corp_schemas
    tariff = await mapping.to_corp_schema(
        tariff, mapping.Schema.IndividualTariffs,
    )
    # добавляем обязательные поля
    tariff['id'] = tariff.pop('_id')
    tariff['categories'][0]['category_name_key'] = 'category_name_key'
    # кастим к тарифу, который находится в ответе corp_tariff
    corp_tariffs.Tariff.deserialize(tariff)
