import { createDialogApi } from './dialog';

describe('createDialogApi', () => {
  test('should open dialog with state', () => {
    const dialog = createDialogApi<{ key: string }>();

    dialog.show({ key: 'value' });
    expect(dialog.$state.getState()).toEqual({ key: 'value' });

    dialog.hide();
    expect(dialog.$state.getState()).toEqual({ key: 'value' });
  });

  test('should reset dialog', () => {
    const dialog = createDialogApi<{ key: string }>();

    dialog.show({ key: 'value' });
    dialog.reset();

    expect(dialog.$state.getState()).toEqual({});
  });

  test('should export dialog key if exists', () => {
    const dialog0 = createDialogApi();
    const dialog1 = createDialogApi('dialog-key');

    expect(dialog0.key).toBe(null);
    expect(dialog1.key).toBe('dialog-key');
  });
});
