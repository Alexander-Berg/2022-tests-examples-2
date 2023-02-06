import * as fs from 'fs';
import * as path from 'path';
import {AppDivOptions} from '../blocks/app-div-options';

/**
 * Получение сохраненнного для тестов ответа ручки ПП-карточки
 * @param id айди карточки
 * @param fetch фетчилка
 * @param opts ПП-параметры
 */
export async function mockResponse<T extends AppDivOptions>(
    id: string,
    fetch: (opts: T) => Promise<any>,
    opts: T
): Promise<any> {
    const _resPath = path.join(__dirname, 'mocks/div', `${id}.response.json`);

    if (fs.existsSync(_resPath)) {
        return JSON.parse(fs.readFileSync(_resPath, {encoding: 'utf-8'})) as unknown;
    } else {
        const data = await fetch(opts) as unknown;

        fs.writeFileSync(_resPath, JSON.stringify(data));

        return data;
    }
}
