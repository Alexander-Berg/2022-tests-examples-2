import {StartrekTable} from './startrek-table'
import type {Table} from './startrek-table'

const TEXT_TABLE = `<table>
   <tbody>
      <tr>
         <td>
            <p>1</p>
         </td>
         <td>
            <p>Были изменения в экспериментах?</p>
         </td>
         <td>
            <p><span style="color: red;">Да</span>/<span style="color: green;">Нет</span></p>
         </td>
         <td>
            <p>
               <ссылка на файл с экспами в ПР>
            </p>
         </td>
      </tr>
      <tr>
         <td>
            <p>2</p>
         </td>
         <td>
            <p>Были изменения в экспериментах?</p>
         </td>
         <td>
            <p><span style="color: red;">Да</span>/<span style="color: green;">Нет</span></p>
         </td>
         <td>
            <p>
               <ссылка на файл с экспами в ПР>
            </p>
         </td>
      </tr>
      <tr>
         <td>
            <p>3</p>
         </td>
         <td>
            <p>Были изменения в экспериментах?</p>
         </td>
         <td>
            <p><span style="color: red;">Да</span>/<span style="color: green;">Нет</span></p>
         </td>
         <td>
            <p>
               <ссылка на файл с экспами в ПР>
            </p>
         </td>
      </tr>
   </tbody>
</table>`
const TEXT_TABLE_ROWS_COUNT = 3

const ROWS_TABLE: Table = {
  entries: [
    [
      '1',
      'Были изменения в экспериментах?',
      '<span style="color: red;">Да</span>/<span style="color: green;">Нет</span>',
      '<ссылка на файл с экспами в ПР>',
    ],
    [
      '2',
      'Были изменения в экспериментах?',
      '<span style="color: red;">Да</span>/<span style="color: green;">Нет</span>',
      '<ссылка на файл с экспами в ПР>',
    ],
    [
      '3',
      'Были изменения в экспериментах?',
      '<span style="color: red;">Да</span>/<span style="color: green;">Нет</span>',
      '<ссылка на файл с экспами в ПР>',
    ],
  ],
}

describe('StartrekTable class', () => {
  it('should create a table from text and rows', () => {
    expect(createTableFromText()).not.toBeUndefined()
    expect(createTableFromRows()).not.toBeUndefined()
  })

  it('should throw when a table without <tbody> tag was provided', () => {
    // constructor
    expect(() => new StartrekTable('<table><thead></thead></table>')).toThrow(
      'Startrek table parse error: <table> must have a <tbody> tag inside.',
    )
    // setter
    expect(() => createTableFromText().setTable('wtf?')).toThrow(
      'Startrek table parse error: <table> must have a <tbody> tag inside.',
    )
  })

  it('should parse the correct amount of rows from the text representation', () => {
    expect(createTableFromText().rows.length).toEqual(TEXT_TABLE_ROWS_COUNT)
  })

  it('should set the "table-id" data-attribute whenever table is set with the TableRow[] and non-empty "id"', () => {
    const textTable = new StartrekTable(
      '<table><tbody><tr><td><p>Hello world</tr></td></p></tbody></table>',
      'my-cool-id',
    )
    const rowTable = new StartrekTable({entries: [['Hello world']]}, 'my-cool-id')

    expect(textTable.getTable()).not.toMatch(/<table table-id=".*?">/im)
    expect(rowTable.getTable()).toMatch(/<table table-id="my-cool-id">/im)

    rowTable.setTable({entries: rowTable.rows}, '')

    expect(rowTable.getTable()).not.toMatch(/<table table-id=".*?">/im)
  })

  it('should parse row data in the same way regardless of input data representation', () => {
    const t1 = createTableFromText()
    const t2 = createTableFromRows()

    expect(t1.rows).toEqual(t2.rows)
  })

  it('should trim row string values', () => {
    const table = new StartrekTable({entries: [[' no space before me', 'no space after me ']]})
    expect(
      table.rows.some(row => {
        for (const value of row) {
          return value.startsWith(' ') || value.endsWith(' ')
        }
      }),
    ).toBe(false)
  })

  it('should find table in a text if there is one', () => {
    expect(StartrekTable.searchForTable('<table></table>')).toBeTruthy()
    expect(StartrekTable.searchForTable('<table table-id="my_cool_id"></table>', 'my_cool_id')).toBeTruthy()

    expect(StartrekTable.searchForTable('<table table-id="my_cool_id"></table>')).toBeFalsy()
    expect(StartrekTable.searchForTable('wtf?')).toBeFalsy()
  })

  it('should be able to append a row', () => {
    const table = createTableFromText()
    table.insertRow([
      '12',
      'Были изменения в экспериментах?',
      '<span style="color: red;">Да</span>/<span style="color: green;">Нет</span>',
      '<ссылка на файл с экспами в ПР #4>',
    ])

    expect(table.rowCount).toBe(4)
    expect(table.rows.slice(-1)[0][0]).toBe('12')
  })

  it('should ignore empty row insertion', () => {
    const table = createTableFromText()
    const initialRowCount = table.rowCount
    // @ts-expect-error [string, ...string[]] type still can't safeguard against empty row insertion
    table.insertRow([])
    // @ts-expect-error [string, ...string[]] type still can't safeguard against empty row insertion
    table.prependRow([])
    expect(table.rowCount).toBe(initialRowCount)
  })

  it('should be able to prepend a row', () => {
    const table = createTableFromText()
    table.prependRow([
      '12',
      'Были изменения в экспериментах?',
      '<span style="color: red;">Да</span>/<span style="color: green;">Нет</span>',
      '<ссылка на файл с экспами в ПР #4>',
    ])

    expect(table.rowCount).toBe(4)
    expect(table.rows[0][0]).toBe('12')
  })

  it('should be able to insert a row according to a comparator', () => {
    const table = createTableFromText()
    table.insertRow(
      [
        '4',
        'Были изменения в экспериментах?',
        '<span style="color: red;">Да</span>/<span style="color: green;">Нет</span>',
        '<ссылка на файл с экспами в ПР #4>',
      ],
      {
        insertionComparator: (tableRow, insertedRow) => (Number(tableRow[0]) < Number(insertedRow[0]) ? 1 : -1),
      },
    )

    expect(table.rowCount).toBe(4)

    table.insertRow(
      [
        '5',
        'Были изменения в экспериментах?',
        '<span style="color: red;">Да</span>/<span style="color: green;">Нет</span>',
        '<ссылка на файл с экспами в ПР #5>',
      ],
      {
        insertionComparator: tableRow => (tableRow[3].includes('<ссылка на файл с экспами в ПР #4>') ? 0 : -1),
      },
    )

    expect(table.rowCount).toBe(5)
    expect(table.rows.map(row => row[0])).toEqual(['4', '5', '1', '2', '3'])
  })
})

function createTableFromText() {
  return new StartrekTable(TEXT_TABLE)
}

function createTableFromRows() {
  return new StartrekTable(ROWS_TABLE)
}
