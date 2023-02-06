import {Modes} from '_sagas/form';
import {DraftModes} from '_types/common/drafts';

import {FormSagaType} from '../enums';
import {getDraftMode} from '../utils';

describe('getDraftMode', () => {
    it('(Modes.Create, FormSagaType.Draft) => DraftModes.CreateDraft', () => {
        expect(getDraftMode(Modes.Create, FormSagaType.Draft)).toEqual(DraftModes.CreateDraft);
    });
    it('(Modes.Create, FormSagaType.Flat) => DraftModes.Create', () => {
        expect(getDraftMode(Modes.Create, FormSagaType.Flat)).toEqual(DraftModes.Create);
    });
    it('(Modes.Copy, FormSagaType.Draft) => DraftModes.CopyDraft', () => {
        expect(getDraftMode(Modes.Copy, FormSagaType.Draft)).toEqual(DraftModes.CopyDraft);
    });
    it('(Modes.Copy, FormSagaType.Flat) => DraftModes.Copy', () => {
        expect(getDraftMode(Modes.Copy, FormSagaType.Flat)).toEqual(DraftModes.Copy);
    });
    it('(Modes.Edit, FormSagaType.Draft) => DraftModes.EditDraft', () => {
        expect(getDraftMode(Modes.Edit, FormSagaType.Draft)).toEqual(DraftModes.EditDraft);
    });
    it('(Modes.Edit, FormSagaType.Flat) => DraftModes.Edit', () => {
        expect(getDraftMode(Modes.Edit, FormSagaType.Flat)).toEqual(DraftModes.Edit);
    });
    it('(Modes.Show, FormSagaType.Draft) => DraftModes.ShowDraft', () => {
        expect(getDraftMode(Modes.Show, FormSagaType.Draft)).toEqual(DraftModes.ShowDraft);
    });
    it('(Modes.Show, FormSagaType.Flat) => DraftModes.Show', () => {
        expect(getDraftMode(Modes.Show, FormSagaType.Flat)).toEqual(DraftModes.Show);
    });
});
