import {put, select} from 'typed-redux-saga';

import {pure as commonActions} from '_infrastructure/actions';
import {getOperation, getStrictModel} from '_infrastructure/selectors';
import {DraftModes} from '_types/common/drafts';

import ScoringScriptsService from '../../../sagas/services/ScoringScriptsService';
import {getInputsRecord} from '../../../sagas/services/utils';
import {ScriptType} from '../../../types';
import {scriptModel} from '../../../utils';

export default {
    onLoad: function* onLoad(type: Undefinable<ScriptType>, mode: DraftModes) {
        if (mode === DraftModes.Create) {
            const {result: interfaces} = yield* select(getOperation(ScoringScriptsService.loadInterfaces.id));
            const currType = interfaces?.find(int => int.script_type === type);
            const tests = yield* select(getStrictModel(scriptModel(m => m.tests)));
            const newInput = getInputsRecord(currType?.test_inputs, '{}');
            const newOutputs = getInputsRecord(currType?.test_outputs);
            const updatedTests = tests.map(test => ({
                name: test.name,
                input: newInput,
                output: newOutputs,
            }));

            yield* put(
                commonActions.form.strict.change(
                    scriptModel(m => m.tests),
                    updatedTests,
                ),
            );
        }
    },
};
