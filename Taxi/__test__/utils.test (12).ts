import {ReturnFuncType} from '_pkg/types/saga';

import {
    FormUnnamedCalculatedTemplateItemParameter,
    TemplateItemParameterArrayFilterValue,
    TemplateParameter,
    UnnamedCalculatedTemplateItemParameter,
} from '../../../types';
import {convertToViewSchema} from '../../../utils';
import {getOperatorFields} from '../utils';

const EMPTY_OPERATOR_PARAM: FormUnnamedCalculatedTemplateItemParameter = {
    type: 'array',
    data_usage: 'CALCULATED',
    value: {}
};

const ITEM_PARAM: UnnamedCalculatedTemplateItemParameter = {
    type: 'array',
    data_usage: 'CALCULATED',
    value: {
        operator: 'MANY_FILTER',
        array: {
            type: 'array',
            data_usage: 'CALCULATED',
            value: {
                operator: 'FILTER',
                array: {type: 'array', data_usage: 'PARENT_TEMPLATE_DATA', value: 'list'},
                path: {type: 'string', data_usage: 'OWN_DATA', value: '#item.obj.str'},
                compared_value: {
                    value: {type: 'object', data_usage: 'PARENT_TEMPLATE_DATA', value: 'obj'},
                    path: {type: 'string', data_usage: 'OWN_DATA', value: '#item.str'}
                }
            }
        },
        path: {type: 'string', data_usage: 'OWN_DATA', value: '#item.obj.str'},
        compared_value: {
            value: {type: 'array', data_usage: 'PARENT_TEMPLATE_DATA', value: 'compared_list'},
            path: {type: 'string', data_usage: 'OWN_DATA', value: '#item.str'}
        }
    },
};

const PARENT_PARAM_LIST: TemplateParameter = {
    name: 'list',
    type: 'array',
    schema: {
        list: {
            type: 'array',
            items: {
                type: 'object',
                properties: {
                    obj: {
                        type: 'object',
                        properties: {
                            list: {
                                type: 'array',
                                items: {
                                    type: 'object',
                                    properties: {str: {type: 'string'}, bool: {type: 'boolean'}}
                                }
                            }, str: {type: 'string'}
                        }
                    }, str: {type: 'string'}, num: {type: 'number'}
                }
            }
        }
    },
    inherited: false,
    enabled: true
};

const PARENT_PARAM_COMPARED_LIST: TemplateParameter = {
    name: 'compared_list',
    type: 'array',
    schema: {
        compared_list: {
            type: 'array',
            items: {type: 'object', properties: {compared_list_str: {type: 'string'}}}
        }
    },
    inherited: false,
    enabled: true
};

const PARENT_PARAM_OBJ: TemplateParameter = {
    name: 'obj',
    type: 'object',
    schema: {obj: {type: 'object', properties: {str: {type: 'string'}}}},
    inherited: false,
    enabled: true
};

const parentParams = [PARENT_PARAM_LIST, PARENT_PARAM_COMPARED_LIST, PARENT_PARAM_OBJ]
    .map(({schema, ...param}) => ({
        ...param,
        schema: convertToViewSchema(schema),
    }));

function getOwnOptions(
    fields: ReturnFuncType<typeof getOperatorFields>
): Record<string, ReturnFuncType<typeof getOperatorFields>[number]> {
    return fields
        .reduce((res, field) => ({
            ...res,
            [field.model]: field
        }), {});
}

describe('TemplateItemParameters utils', () => {
    describe('getOperatorFields', () => {
        test('правильно строит options для MANY_FILTER', () => {
            const fields = getOperatorFields(ITEM_PARAM, parentParams, {});
            const fieldsMapByModel = getOwnOptions(fields);

            const expectedPathOptions = [
                {value: '#item.obj.str', label: '#item.obj.str'},
                {value: '#item.str', label: '#item.str'}
            ];

            const comparedValuePathOptions = [{value: '#item.compared_list_str', label: '#item.compared_list_str'}];

            expect(fieldsMapByModel.path.ownDataOptions).toEqual(expectedPathOptions);
            expect(fieldsMapByModel['compared_value.path'].ownDataOptions).toEqual(comparedValuePathOptions);
        });

        test('правильно строит options для FILTER', () => {
            const value = ITEM_PARAM.value as TemplateItemParameterArrayFilterValue;
            const fields = getOperatorFields(
                value.array as UnnamedCalculatedTemplateItemParameter,
                parentParams,
                {},
                undefined
            );
            const fieldsMapByModel = getOwnOptions(fields);

            const expectedPathOptions = [
                {value: '#item.obj.str', label: '#item.obj.str'},
                {value: '#item.str', label: '#item.str'}
            ];

            const comparedValuePathOptions = [{value: '#item.str', label: '#item.str'}];

            expect(fieldsMapByModel.path.ownDataOptions).toEqual(expectedPathOptions);
            expect(fieldsMapByModel['compared_value.path'].ownDataOptions).toEqual(comparedValuePathOptions);
        });

        test('возвращает пустой массив при невыбранной операции', () => {
            expect(getOperatorFields(EMPTY_OPERATOR_PARAM, [], {})).toEqual([]);
        });
    });
});
