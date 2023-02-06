import {DraftCommonFieldsModel} from '_libs/drafts/types';

import {getErrors} from '../draftUtils';

describe('getErrors', () => {
    test('должна выдавать ошибку, если описание название нового тикета введено, а описание нет', () => {
        const model: Partial<DraftCommonFieldsModel> = {
            ticketSummary: 'ticket summary'
        };
        const result = getErrors(model, 'ticketDescription');

        expect(typeof result.ticketDescription).toEqual('string');
    });
});
