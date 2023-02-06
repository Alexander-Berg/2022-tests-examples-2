import fs from 'fs';
import nock from 'nock';
import path from 'path';
import stringify from 'safe-stable-stringify';

import {serviceResolve} from '@/src/lib/resolve';
import {matchTextToTable} from 'server/recognition/match-text';
import {recognizeDocuments} from 'server/recognition/recognize-document';
import type {CorrectDocument, OcrTextFromOnePage, TextRectPage} from 'server/recognition/types/types';
import {getRectsAndOcrDataForPages} from 'service/recognize-pdf-pages';
import {getSortOrder} from 'service/utils/array';
import {mapIfNotUndefined} from 'service/utils/map-if-undefined';
import {mapObject} from 'service/utils/object/map-object/map-object';
import {tryAndMapResult} from 'service/utils/try-and-map-result';
import type {CorrectDocumentType} from 'types/documents';
import {RecognitionResultStatus} from 'types/recognition-results';

export async function runRecognitionFlow(
    dirPath: string,
    type: CorrectDocumentType,
    inn: string,
    tableWithTextPages?: TextRectPage[],
    textRecognizedPages?: OcrTextFromOnePage[]
) {
    if (textRecognizedPages === undefined || tableWithTextPages === undefined) {
        const buffer = fs.readFileSync(path.join(dirPath, 'actual.pdf'));
        const {pagesTexts, pagesRects} = await getRectsAndOcrDataForPages(
            buffer,
            300,
            {id: 1, taskId: 1},
            path.join(dirPath, 'images')
        );
        tableWithTextPages = matchTextToTable({pagesTexts, pagesRects});
        textRecognizedPages = pagesTexts.map((page: {data: OcrTextFromOnePage}) => page['data']);
    }

    return {
        result: recognizeDocuments({
            textRectPages: tableWithTextPages,
            textRecognizedPages,
            documentType: type,
            auxiliaryData: {erpInn: inn}
        }),
        tableWithTextPages,
        textRecognizedPages
    };
}

async function runTest(
    dirPath: string
): Promise<{
    json: CorrectDocument | {};
    expected: Required<CorrectDocument>;
}> {
    const expected: Required<CorrectDocument> = JSON.parse(
        fs.readFileSync(path.join(dirPath, 'expected.json')).toString()
    );
    const {type, inn} = expected;

    const tableWithTextPages: TextRectPage[] | undefined = tryAndMapResult(() =>
        JSON.parse(fs.readFileSync(path.join(dirPath, 'table-pages.json')).toString())
    );
    const textRecognizedPages: OcrTextFromOnePage[] | undefined = tryAndMapResult(() =>
        JSON.parse(fs.readFileSync(path.join(dirPath, 'text-pages.json')).toString())
    );

    nock.enableNetConnect();

    const {
        result,
        tableWithTextPages: newTableWithTextPages,
        textRecognizedPages: newTextRecognizedPages
    } = await runRecognitionFlow(dirPath, type, inn, tableWithTextPages, textRecognizedPages);

    nock.disableNetConnect();

    if (textRecognizedPages === undefined) {
        fs.writeFileSync(path.join(dirPath, 'text-pages.json'), stringify(newTextRecognizedPages, null, 4));
    }

    if (tableWithTextPages === undefined) {
        fs.writeFileSync(path.join(dirPath, 'table-pages.json'), stringify(newTableWithTextPages, null, 4));
    }

    return {
        json:
            result.status === RecognitionResultStatus.SUCCESS
                ? getUsefulDataFromRecognitionResult(result.json as CorrectDocument)
                : {},
        expected
    };
}

function getUsefulDataFromRecognitionResult(result: CorrectDocument): CorrectDocument {
    return {...result, pages: result.pages.map((page) => ({...page, rawTable: []}))};
}

describe('integration', () => {
    const basePath = serviceResolve('./src/server/recognition/samples/integration');
    const dirs = fs.readdirSync(basePath).sort(getSortOrder('asc', Number));

    dirs.forEach((dir) => {
        if (!dir.match(new RegExp(/^\d+$/))) {
            return;
        }

        it(`${dir}`, async () => {
            // eslint-disable-next-line no-console
            console.log('run test:', dir);

            const fullPath = path.join(basePath, dir);
            const {json, expected} = await runTest(fullPath);

            expect(json).not.toStrictEqual({});

            const document: CorrectDocument = json as CorrectDocument;

            // fs.writeFileSync(
            //     path.join(fullPath, 'expected.json'),
            //     stringify(
            //         {
            //             ...document,
            //             pages: document.pages.map((p) => ({
            //                 ...p,
            //                 items: p.items.map((item) => mapObject(item, (value) => value.toFormattedString())),
            //                 pageTotal: mapIfNotUndefined(p.pageTotal, (pageTotal) =>
            //                     mapObject(pageTotal, (value) => value.toFormattedString())
            //                 )
            //             })),
            //             total: mapIfNotUndefined(document.total, (total) =>
            //                 mapObject(total, (value) => value.toFormattedString())
            //             )
            //         },
            //         null,
            //         4
            //     )
            // );

            expect({
                pages: document.pages.map((p) =>
                    p.items.map((item) => mapObject(item, (value) => value.toFormattedString()))
                ),
                pageTotals: document.pages.map((p) =>
                    mapIfNotUndefined(p.pageTotal, (pageTotal) =>
                        mapObject(pageTotal, (value) => value.toFormattedString())
                    )
                ),
                date: document.date,
                inn: document.inn,
                total: mapIfNotUndefined(document.total, (total) =>
                    mapObject(total, (value) => value.toFormattedString())
                )
            }).toEqual({
                pages: expected.pages.map((p) => p.items),
                pageTotals: expected.pages.map((p) => p.pageTotal),
                date: mapIfNotUndefined(expected.date, (date) => new Date(date)),
                inn: expected.inn,
                total: expected.total
            });
        }, 170000);
    });
});
