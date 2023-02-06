import {call} from 'typed-redux-saga';

import {FormMode, TabType} from '../../enums';
import EntityService from '../../sagas/services/EntityService';

export const saga = {
    onLoad: function* (tabType: TabType, mode: FormMode, id: Undefinable<string>) {
        yield* call(EntityService.loadEntityModel, tabType, mode, id);
    },
};
