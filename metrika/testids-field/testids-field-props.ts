import { FieldRenderProps } from 'react-final-form';

export interface TestIdsFieldItemValue {
    id?: number;
    name: string;
    description?: string;
    value?: [string, string][];
}

export interface TestIdsFieldProps extends FieldRenderProps<TestIdsFieldItemValue[], HTMLDivElement> {
    isDisabled?: boolean;
}
