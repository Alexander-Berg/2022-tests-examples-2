import {CircuitSchemaJson} from '_pkg/api/hejmdal-debug/types';
import {TestCaseList, TestCaseListItem} from '_pkg/api/hejmdal-test-case/types';

export * from '_pkg/api/hejmdal-test-case/types';
export * from '_pkg/api/hejmdal-debug/types';

export enum TestStatus {
    Success,
    Error,
    Default
}

export interface HejmdalModalLoadArgs {
    schemaId: string;
    schemaJson: CircuitSchemaJson;
    onDebug: (id: number) => void;
}

export type SelectedMap = Record<number, boolean>;

export interface HejmdalTestingModel {
    enabled: SelectedMap;
    disabled: SelectedMap;
}

export type TestsListItem = Assign<
    TestCaseListItem,
    {
        status?: TestStatus;
    }
>;

export type TestsList = Assign<
    TestCaseList,
    {
        enabled: TestsListItem[];
        disabled: TestsListItem[];
    }
>;
