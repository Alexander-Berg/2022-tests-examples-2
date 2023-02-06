import Button from 'amber-blocks/button';
import React, {FC, Fragment, memo, useCallback, useMemo} from 'react';

import {AmberField} from '_blocks/form';
import {Col, Row} from '_blocks/row';
import useStrictModel from '_hooks/use-strict-model';
import modelPath, {PathFn} from '_utils/modelPath';
import objectEntries from '_utils/objectEntries';
import {isNotEmpty} from '_utils/strict/validators';

import {DOT, LABELS} from '../../../consts';
import {TestDataPart} from '../../../enums';
import {service} from '../../../sagas/services/ScoringScriptsService';
import {ScriptTest} from '../../../types';
import InputProp from './InputProp';
import {getTestErrorMaps} from './utils';

import {b} from './Tests.styl';

type Props = {
    testsPathFn: PathFn<Array<ScriptTest>>;
    index: number;
    disabled: boolean;
};

const Test: FC<Props> = ({testsPathFn, index, disabled}) => {
    const testPathFn = useMemo(() => modelPath(testsPathFn(m => m[index])), [testsPathFn, index]);
    const handleRemoveTest = useCallback(() => service.actions.removeTest(index), [index]);
    const test = useStrictModel(testPathFn(m => m));
    const [testInputErrorsMap, testOutputErrorsMap] = useMemo(() => getTestErrorMaps(test.errors), [test.errors]);
    const commonErrors = useMemo(
        () => [...(testInputErrorsMap[TestDataPart.Input] ?? []), ...(testOutputErrorsMap[TestDataPart.Output] ?? [])],
        [testInputErrorsMap, testOutputErrorsMap],
    );
    const createTestInputHandler = useCallback(
        (errorGroupName: string) => () => service.actions.removeTestErrors(index, errorGroupName),
        [index, test.errors],
    );

    return (
        <Fragment>
            <Row mode="flex" justify className={b('testRow')}>
                <Col stretch>
                    <label className={b('label')}>{LABELS.NAME}</label>
                    <Row gap="no" className={b('nameWrapper')}>
                        <Col stretch>
                            <AmberField.text
                                model={testPathFn(m => m.name)}
                                disabled={disabled}
                                className={b('name')}
                            />
                        </Col>
                        {!disabled && (
                            <Col>
                                <Button onClick={handleRemoveTest}>{LABELS.REMOVE}</Button>
                            </Col>
                        )}
                    </Row>
                </Col>
            </Row>

            <Row nocols>
                {isNotEmpty(commonErrors) && <div className={b('commonErrors')}>{LABELS.COMMON_ERRORS}:</div>}
                {commonErrors.map(error => (
                    <p key={error.name} className={b('commonErrors')}>
                        {error?.description ?? error.name}
                    </p>
                ))}
                <label className={b('label')}>{LABELS.INPUT}</label>
                <Row gap="no">
                    <Col className={b('jsonCol')}>
                        {objectEntries(test.input).map(([inputPropKey], idx) => (
                            <InputProp
                                key={idx}
                                disabled={disabled}
                                propKey={inputPropKey}
                                inputPathFn={modelPath(testPathFn(m => m.input[inputPropKey]))}
                                errors={testInputErrorsMap[inputPropKey]}
                                onInput={
                                    isNotEmpty(testInputErrorsMap)
                                        ? createTestInputHandler(`${TestDataPart.Input}${DOT}${inputPropKey}`)
                                        : undefined
                                }
                            />
                        ))}
                    </Col>
                    <Col className={b('jsonCol')}>
                        {objectEntries(test.output).map(([outputPropKey], idx) => (
                            <InputProp
                                key={idx}
                                disabled={disabled}
                                propKey={outputPropKey}
                                inputPathFn={modelPath(testPathFn(m => m.output[outputPropKey]))}
                                errors={testOutputErrorsMap[outputPropKey]}
                                onInput={
                                    isNotEmpty(testOutputErrorsMap)
                                        ? createTestInputHandler(`${TestDataPart.Output}${DOT}${outputPropKey}`)
                                        : undefined
                                }
                            />
                        ))}
                    </Col>
                </Row>
            </Row>
        </Fragment>
    );
};

export default memo(Test);
