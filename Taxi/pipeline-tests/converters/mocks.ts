import {head} from 'lodash';
import uuid from 'uuid';

import {jsonParse} from '_utils/parser';
import {prettyJSONStringify} from '_utils/prettyJSONStringify';
import {isEmpty} from '_utils/strict/validators';
import {toRequestParamValue} from '_utils/toRequestParamValue';

import {
    InputMocks,
    Mock,
    MockModel,
    PipelineTest,
    PrefetchedResourcesMocks,
    Resource,
    ResourcesMocks,
    TestMockModel,
} from '../types';
import {isPrefetchedResource} from '../utils';

export const prepareMockModel = ({resource = '', name, mock, is_prefetched}: Mock): MockModel => {
    const code = resource && !is_prefetched ? mock.mock_body : prettyJSONStringify(mock);

    return {
        mockName: name,
        isResourceMock: !!resource,
        resource: resource,
        code,
    };
};

export const prepareMock = ({mockName, resource, code}: MockModel, resources: Resource[], id: string): Mock => {
    const isPrefetched = isPrefetchedResource(resource, resources);
    return {
        id,
        name: mockName,
        is_prefetched: isPrefetched,
        resource: toRequestParamValue(resource),
        mock: resource && !isPrefetched ? {mock_body: code} : jsonParse(code),
    };
};

export const preparePrefetchedMocks = (prefetchedMocks: Undefinable<PrefetchedResourcesMocks>): TestMockModel[] => {
    return Object.entries(prefetchedMocks ?? {}).map(([resource, prefetchedMock]) => {
        const [mockName = '', code] = head(Object.entries(prefetchedMock)) ?? [];

        return {
            _id: uuid.v4(),
            isResourceMock: true,
            resource,
            mockName: mockName ?? '',
            code: code ? prettyJSONStringify(code) : '',
        };
    });
};

export const prepareResourcedMocks = (resourceMocks: Undefinable<ResourcesMocks>): TestMockModel[] => {
    return Object.entries(resourceMocks ?? {}).map(([resouce, resourceMock]) => {

        const [mockName, mock] = head(Object.entries(resourceMock)) ?? [];

        return {
            _id: uuid.v4(),
            isResourceMock: true,
            resource: resouce ?? '',
            mockName: mockName ?? '',
            code: mock?.mock_body ?? '',
        };
    });
};

export const prepareInputMocks = (inputMocks: Undefinable<InputMocks>): TestMockModel[] => {
    return Object.entries(inputMocks ?? {}).map(([mockName, code]) => {
        return {
            _id: uuid.v4(),
            isResourceMock: false,
            resource: '',
            mockName,
            code: prettyJSONStringify(code),
        };
    });
};

export const prepareTestMockModels = (mocks: TestMockModel[], resources: Resource[]) => {
    return mocks.reduce<Pick<PipelineTest, 'input_mocks' | 'resources_mocks' | 'prefetched_resources_mocks'>>(
        (acc, mock) => {
            if (isEmpty(mock.resource)) {
                if (acc.input_mocks === undefined) {
                    acc.input_mocks = {};
                }
                acc.input_mocks[mock.mockName] = jsonParse(mock.code);
            } else {
                if (isPrefetchedResource(mock.resource, resources)) {
                    if (acc.prefetched_resources_mocks === undefined) {
                        acc.prefetched_resources_mocks = {};
                    }
                    acc.prefetched_resources_mocks[mock.resource] = {
                        [mock.mockName]: jsonParse(mock.code),
                    };
                } else {
                    if (acc.resources_mocks === undefined) {
                        acc.resources_mocks = {};
                    }
                    acc.resources_mocks[mock.resource] = {[mock.mockName]: {mock_body: mock.code}};
                }
            }
            return acc;
        },
        {},
    );
};
