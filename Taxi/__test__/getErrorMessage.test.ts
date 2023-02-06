import {ServerError} from '_pkg/utils/errors';
import getErrorMessage from '_pkg/utils/errors/getErrorMessage';

describe('getErrorMessage', () => {
    test('удаляет все html теги', () => {
        const MESSAGE = 'MESSAGE';
        const CODE = 'CODE';
        const err = new ServerError('', {
            res: {
                status: 400,
                statusText: '',
                headers: [],
                config: null!,
                data: {
                    message: `<b>${MESSAGE}</b>`,
                    code: CODE
                }
            }
        });

        const commonErr = new Error('xxx');

        expect(getErrorMessage(commonErr)).toEqual(String(commonErr));
        expect(getErrorMessage(err)).toEqual(`[${CODE}] ${MESSAGE}`);
        expect(getErrorMessage(`<a href="/"><b><i>${MESSAGE}</i></b></a>`)).toEqual(MESSAGE);
        expect(getErrorMessage(`""${MESSAGE}''`)).toEqual(`""${MESSAGE}''`);
    });

    // TODO настроить локализацию для тестов
    // test('ошибка по умолчанию', () => {
    //     expect(getErrorMessage('')).toEqual('Неизвестная ошибка на бекенде!');
    // });
});
