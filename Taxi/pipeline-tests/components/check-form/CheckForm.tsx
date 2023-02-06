import React, {FC, Fragment, memo, useMemo} from 'react';

import {AmberField, Form} from '_blocks/form';
import {FormLayoutSimple} from '_blocks/form-layout';
import JSEditor from '_blocks/form/amber-field/code-editor/JSEditor';
import JSONEditorField from '_blocks/form/amber-field/code-editor/JSONEditorField';
import {Row} from '_blocks/row';
import {useIsFormDisabled} from '_hooks/use-is-form-disabled';
import useStrictModel from '_hooks/use-strict-model';
import ValidationErrors from '_pkg/blocks/validation-errors';
import {StrictModel} from '_types/common/infrastructure';
import modelPath from '_utils/modelPath';

import {MAX_JS_CODE_ROWS, MIN_JS_CODE_ROWS} from '../../../common/consts';
import {LABELS} from '../../consts';
import {CheckType} from '../../enums';
import {CheckModel} from '../../types';

import {b} from './CheckForm.styl';

type Props = {
    model: StrictModel<CheckModel>;
};

const OPTIONS = [
    {label: LABELS.COMBINED, value: CheckType.Combined},
    {label: LABELS.IMPERATIVE, value: CheckType.Imperative},
];

const CheckForm: FC<Props> = ({model}) => {
    const path = useMemo(() => modelPath(model), [model]);
    const disabled = useIsFormDisabled();
    const {checkType} = useStrictModel(model);
    const isCombineType = checkType === CheckType.Combined;
    return (
        <Form model={model}>
            <FormLayoutSimple label={LABELS.NAME}>
                <AmberField.text model={path(m => m.checkName)} />
            </FormLayoutSimple>
            <FormLayoutSimple label={LABELS.TYPE} flex>
                <AmberField.radioButton model={path(m => m.checkType)} options={OPTIONS} />
            </FormLayoutSimple>
            <FormLayoutSimple label={LABELS.CODE} flex>
                {isCombineType && (
                    <Fragment>
                        <Row className={b('codeTitle')} gap="s">
                            {LABELS.JSON}
                        </Row>
                        <JSONEditorField
                            model={path(m => m.code)}
                            minLines={MIN_JS_CODE_ROWS}
                            maxLines={MAX_JS_CODE_ROWS}
                            readOnly={disabled}
                        />
                        <ValidationErrors model={path(m => m.code)} />
                    </Fragment>
                )}
                {!isCombineType && (
                    <Fragment>
                        <Row className={b('codeTitle')} gap="s">
                            {LABELS.FUNCTION_OUTPUT}
                        </Row>
                        <JSEditor
                            model={path(m => m.code)}
                            minLines={MIN_JS_CODE_ROWS}
                            maxLines={MAX_JS_CODE_ROWS}
                            readOnly={disabled}
                        />
                        <ValidationErrors model={path(m => m.code)} />
                        <Row>{`}`}</Row>
                    </Fragment>
                )}
            </FormLayoutSimple>
            {isCombineType && (
                <FormLayoutSimple flex>
                    <AmberField.checkbox
                        model={path(m => m.ignoreAdditionalParams)}
                        label={LABELS.IGNORE_ADDITIONAL_PARAMS}
                    />
                </FormLayoutSimple>
            )}
        </Form>
    );
};

export default memo(CheckForm);
