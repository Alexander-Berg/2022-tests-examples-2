import {Tab, Tabs} from 'amber-blocks/tabs';
import {isEqual} from 'lodash';
import React, {FC, Fragment, memo, useCallback, useMemo, useState} from 'react';
import {useSelector} from 'react-redux';

import AsyncContent from '_blocks/async-content';
import useSaga from '_hooks/use-saga';
import useStrictModel from '_hooks/use-strict-model';
import {getField} from '_reducers/formReducer';
import {DraftModes} from '_types/common/drafts';
import {StrictModel} from '_types/common/infrastructure';
import modelPath from '_utils/modelPath';
import {isNotEmpty} from '_utils/strict/validators';

import {LABELS} from '../../../consts';
import {BundleState, ScriptTest} from '../../../types';
import {scriptModel} from '../../../utils';
import saga from './saga';
import Test from './Test';

import {b} from './Tests.styl';

type Props = {
    testsModel: StrictModel<Array<ScriptTest>>;
    disabled: boolean;
    mode: DraftModes;
};

const Tests: FC<Props> = ({testsModel, disabled, mode}) => {
    const [tab, setTab] = useState<number>(0);
    const type = useStrictModel(scriptModel(m => m.type));
    const {operationId} = useSaga(saga, [type, mode]);
    const testsModelPath = useMemo(() => modelPath(testsModel), [testsModel]);
    const tests = useStrictModel(testsModelPath(m => m));
    const handleChangeTab = useCallback((val: number) => {
        setTab(val);
    }, []);
    const errors = useSelector(
        (state: BundleState) => {
            return tests.map((_, idx) => {
                const {errors} =
                    getField(
                        state as any,
                        scriptModel(m => m.tests[idx]),
                    ) ?? {};

                return errors;
            });
        },
        (prev: Array<any>, next: Array<any>) => isEqual(prev, next),
    );
    const tabs = useMemo(
        () =>
            tests.map((_, index) => {
                const isCurrError = errors[index];
                const currClassName = b('tab', {error: isCurrError === true, success: isCurrError === false});

                return <Tab className={currClassName} key={index} tabname={`${LABELS.TEST} #${index + 1}`} />;
            }),
        [tests, errors],
    );

    return (
        <AsyncContent id={operationId}>
            {isNotEmpty(tests) && (
                <Fragment>
                    <Tabs className={b('tabs')} onChange={handleChangeTab}>
                        {tabs}
                    </Tabs>
                    {tab < tests.length && <Test testsPathFn={testsModelPath} index={tab} disabled={disabled} />}
                </Fragment>
            )}
        </AsyncContent>
    );
};

export default memo(Tests);
