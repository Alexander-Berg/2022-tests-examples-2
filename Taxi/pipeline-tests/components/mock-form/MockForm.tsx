import React, {FC, memo, useCallback, useMemo} from 'react';

import {AmberField, Form} from '_blocks/form';
import {FormLayoutSimple} from '_blocks/form-layout';
import JSEditor from '_blocks/form/amber-field/code-editor/JSEditor';
import JSONEditorField from '_blocks/form/amber-field/code-editor/JSONEditorField';
import {useIsFormDisabled} from '_hooks/use-is-form-disabled';
import useOperation from '_hooks/use-operation';
import useStrictModel from '_hooks/use-strict-model';
import {binded as commonActions} from '_infrastructure/actions';
import ValidationErrors from '_pkg/blocks/validation-errors';
import {StrictModel} from '_types/common/infrastructure';
import modelPath from '_utils/modelPath';

import ResourceSelect from '../../../common/components/resource-select';
import {MAX_JS_CODE_ROWS, MIN_JS_CODE_ROWS} from '../../../common/consts';
import {LOAD_RESOURCES_ID} from '../../../common/sagas/services/PipelineCommonService';
import {LABELS} from '../../consts';
import {FormMode} from '../../enums';
import {MockModel} from '../../types';
import {isPrefetchedResource} from '../../utils';

type Props = {
    model: StrictModel<MockModel>;
    mode?: FormMode;
};

const OPTIONS = [
    {label: LABELS.INPUT_MOCK, value: false},
    {label: LABELS.RESOURCE_MOCK, value: true},
];

const MockForm: FC<Props> = ({model, mode}) => {
    const path = useMemo(() => modelPath(model), [model]);

    const modelData = useStrictModel(model);
    const {isResourceMock, resource} = modelData;

    const {result: resources = []} = useOperation({operationId: LOAD_RESOURCES_ID});

    const isPrefetched = useMemo(() => isPrefetchedResource(resource, resources), [resource, resources]);
    const isJavascriptMode = !!resource && !isPrefetched;
    const mockTitle = `${LABELS.MOCK} (${isJavascriptMode ? LABELS.JAVASCRIPT : LABELS.JSON})`;
    const disabled = useIsFormDisabled();
    const disabledInEditMode = mode === FormMode.Edit || disabled;
    const disabledResourceSelector = !isResourceMock || disabledInEditMode;

    const handleChangeMockType = useCallback(
        (_, value: boolean) => {
            commonActions.form.strict.change(model, {
                ...modelData,
                ...(value
                    ? {}
                    : {
                          resource: '',
                      }),
                isResourceMock: value,
            });
        },
        [model, modelData],
    );

    return (
        <Form model={model}>
            <FormLayoutSimple label={LABELS.NAME}>
                <AmberField.text model={path(m => m.mockName)} />
            </FormLayoutSimple>
            <FormLayoutSimple label={LABELS.TYPE} flex>
                <AmberField.radioButton
                    model={path(m => m.isResourceMock)}
                    options={OPTIONS}
                    changeAction={handleChangeMockType}
                    disabled={disabledInEditMode}
                />
            </FormLayoutSimple>
            <FormLayoutSimple label={LABELS.RESOURCE}>
                <ResourceSelect model={path(m => m.resource)} disabled={disabledResourceSelector} />
            </FormLayoutSimple>
            <FormLayoutSimple label={mockTitle} flex>
                {isJavascriptMode ? (
                    <JSEditor
                        model={path(m => m.code)}
                        minLines={MIN_JS_CODE_ROWS}
                        maxLines={MAX_JS_CODE_ROWS}
                        readOnly={disabled}
                    />
                ) : (
                    <JSONEditorField
                        model={path(m => m.code)}
                        minLines={MIN_JS_CODE_ROWS}
                        maxLines={MAX_JS_CODE_ROWS}
                        readOnly={disabled}
                    />
                )}
                <ValidationErrors model={path(m => m.code)} />
            </FormLayoutSimple>
        </Form>
    );
};

export default memo(MockForm);
