import Button from 'amber-blocks/button';
import Plus from 'amber-blocks/icon/Plus';
import Trash from 'amber-blocks/icon/Trash';
import React, {FC, memo, useCallback, useMemo} from 'react';
import {IAnnotation, IMarker} from 'react-ace/lib/types';

import JSONEditorField from '_blocks/form/amber-field/code-editor/JSONEditorField';
import {Col, Row} from '_blocks/row';
import useStrictModel from '_hooks/use-strict-model';
import {binded as commonActions} from '_infrastructure/actions';
import {PathFn} from '_utils/modelPath';
import {isEmpty, isNotEmpty} from '_utils/strict/validators';

import {DOT} from '../../../consts';
import {ExtendedTestErrorDescription, InputProp, TestErrorLine} from '../../../types';
import {ALL_AFTER_SQUARE_BRACKET, ALL_TILL_FIRST_DOT, EMPTY_STRING, NEW_LINE} from './consts';

import {b} from './Tests.styl';

type Props = {
    disabled: boolean;
    propKey: string;
    inputPathFn: PathFn<InputProp>;
    errors?: ExtendedTestErrorDescription[];
    onInput?: () => void;
};

const trashIcon = <Trash />;
const plusIcon = <Plus />;
const MIN_LINES = 3;
const MAX_LINES = 15;

const getMarkers = (errorLines: TestErrorLine[]) => {
    const markers: IMarker[] = [];
    errorLines.forEach(line => {
        markers.push({
            startRow: line.number,
            startCol: 1,
            endRow: line.number,
            endCol: Infinity,
            className: b('errorLine'),
            type: 'fullLine',
        });
    });
    return markers;
};

const getAnnotations = (errorLines: TestErrorLine[]) => {
    const annotations: IAnnotation[] = [];
    errorLines.forEach(line => {
        annotations.push({
            row: line.number,
            column: 0,
            text: line.error ?? EMPTY_STRING,
            type: 'error',
        });
    });
    return annotations;
};

const InputProp: FC<Props> = ({disabled, propKey, inputPathFn, errors, onInput}) => {
    const {enabled: isTestEnabled, value} = useStrictModel(inputPathFn(m => m));
    const handleButtonClick = useCallback(() => {
        commonActions.form.strict.change(
            inputPathFn(m => m.enabled),
            !isTestEnabled,
        );
    }, [inputPathFn, isTestEnabled]);
    const totalError = useMemo(() => errors?.find(error => error.errorKey === propKey), [errors, propKey]);
    const errorLines = useMemo(() => {
        if (isEmpty(errors)) {
            return [];
        }
        const valueLines = value.split(NEW_LINE);
        return errors?.reduce<TestErrorLine[]>((acc, error) => {
            valueLines.forEach((line, lineNumber) => {
                const propPath = error.errorKey.split(DOT);
                if (line.includes(`"${propPath[0]}"`)) {
                    acc.push({
                        number: lineNumber,
                        error:
                            propPath.length > 1
                                ? `${error.errorKey.replace(ALL_TILL_FIRST_DOT, EMPTY_STRING)} - ${error.description}`
                                : error.description,
                    });
                } else if (line.includes(`"${error.errorKey.replace(ALL_AFTER_SQUARE_BRACKET, EMPTY_STRING)}": [`)) {
                    acc.push({
                        number: lineNumber,
                        error: `${error.errorKey.slice(
                            error.errorKey.indexOf('['),
                            error.errorKey.indexOf(']') + 1,
                        )} - ${error.description}`,
                    });
                }
            });
            return acc;
        }, []);
    }, [errors]);
    const markers = useMemo(() => getMarkers(errorLines), [errorLines]);
    const annotations = useMemo(() => getAnnotations(errorLines), [errorLines]);

    return (
        <Row nocols className={b('json')}>
            <label>{propKey}:</label>
            <Row className={b('content', {error: isNotEmpty(totalError)})} verticalAlign="bottom">
                {isTestEnabled && (
                    <Col stretch>
                        <JSONEditorField
                            model={inputPathFn(m => m.value)}
                            readOnly={disabled}
                            minLines={MIN_LINES}
                            maxLines={MAX_LINES}
                            annotations={annotations}
                            markers={markers}
                            onInput={onInput}
                        />
                    </Col>
                )}
                {!disabled && (
                    <Col>
                        <Button icon={isTestEnabled ? trashIcon : plusIcon} onClick={handleButtonClick} />
                    </Col>
                )}
            </Row>
            {isNotEmpty(totalError) && <p className={b('totalError')}>{totalError.description}</p>}
        </Row>
    );
};

export default memo(InputProp);
