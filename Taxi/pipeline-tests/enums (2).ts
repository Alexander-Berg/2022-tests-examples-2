export * from '../common/enums';

export enum TabType {
    Mock = 'mock',
    Check = 'check',
    Test = 'test',
}

export enum FormMode {
    Create = 'create',
    View = 'view',
    Edit = 'edit',
}

export enum CheckType {
    Combined = 'combined',
    Imperative = 'imperative',
}

export enum TestSubmode {
    MockEdit = 'mockEdit',
    CheckEdit = 'checkEdit',
}
