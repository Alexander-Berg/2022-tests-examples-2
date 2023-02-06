import got from 'got';

import assertDefined from '@/src/utils/assert-defined';

interface GetDownloadedFileOptions {
    purge?: boolean;
}

/**
 * @description Запрашивает и возвращает скачанный через браузер файл по имени
 * @param options.purge - Удалить файл из контейнера браузера сразу после скачивания
 * @returns
 */
export async function getDownloadedFile(
    this: WebdriverIO.Browser,
    fileName: string,
    options?: GetDownloadedFileOptions
) {
    const file = await got(buildBrowserApiUrl(this.sessionId, fileName), {retry: {limit: 3, statusCodes: [404]}});
    if (options?.purge) {
        await deleteDownloadedFile.call(this, fileName);
    }
    return file.rawBody;
}

/**
 * @description Удаляет скачанный через браузер файл по имени
 * @returns
 */
export async function deleteDownloadedFile(this: WebdriverIO.Browser, fileName: string) {
    return got(buildBrowserApiUrl(this.sessionId, fileName), {method: 'DELETE', retry: 3});
}

function buildBrowserApiUrl(sessionId: string, fileName: string) {
    return [assertDefined(process.env.SELENOID_DOMAIN), 'download', sessionId, fileName].join('/');
}

export type GetDownloadedFile = typeof getDownloadedFile;
export type DeleteDownloadedFile = typeof deleteDownloadedFile;
