import {read, utils} from 'xlsx';

export function parseSpreadSheetJSON(file: Buffer) {
    const workBook = read(file);
    const content = utils.sheet_to_json(workBook.Sheets[workBook.SheetNames[0]]);
    return content;
}

export function parseSpreadSheetCSV(file: Buffer) {
    const workBook = read(file);
    const content = utils.sheet_to_csv(workBook.Sheets[workBook.SheetNames[0]]);
    return content;
}
