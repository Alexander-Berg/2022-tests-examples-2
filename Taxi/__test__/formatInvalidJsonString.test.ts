import {jsonParse, jsonToString} from '_utils/parser';

import {formatInvalidJsonString} from '../utils';

const SOME_OBJ: any = {
    field1: 123.456,
    field2: 'value',
    field3: true,
    field4: false,
    field5: null,
    field6: [],
    field7: ['string', true, false, null, ['string', true, false, null]],
    field8: {
        field1: {
            field1: 123.456,
            field2: 'value',
            field3: true,
            field4: false,
            field5: null,
            field6: [],
            field7: ['string', true, false, null, ['string', true, false, null]]
        }
    }
};

const VALID_JSON_STR = `{"field2":"value","field3":true,"field6":[],"field7":["string",["string"]],"MARKER1":{"field1":{"field1":123.456,"field6":[],"field7":["string",[[],[],{},{}]]}}}`;

const JSON_STR_FROMATTED = `{
  "field2": "value",
  "field3": true,
  "field6": [
  ],
  "field7": [
    "string",
    [
      "string"
    ]
  ],
  "MARKER1": {
    "field1": {
      "field1": 123.456,
      "field6": [
      ],
      "field7": [
        "string",
        [
          [
          ],
          [
          ],
          {
          },
          {
          }
        ]
      ]
    }
  }
}`;

const INVALID_END = `...(truncated, total 9999 bytes)`;
const PLAIN_TEXT_MARKER = '...(truncated, total';

describe('formatInvalidJsonString', () => {
    test('формат совпадает с jsonToString', () => {
        const inputString = JSON.stringify(SOME_OBJ);

        expect(formatInvalidJsonString(inputString, PLAIN_TEXT_MARKER)).toEqual(jsonToString(jsonParse(inputString)));
    });

    test('правильно формирует строку если json оборван', () => {
        const input = formatInvalidJsonString(
            `{"field2":"value","field3":true,"field6":[],"field7":["string",` + INVALID_END,
            PLAIN_TEXT_MARKER
        );

        const result =
            `{
  "field2": "value",
  "field3": true,
  "field6": [
  ],
  "field7": [
    "string",
    ` + INVALID_END;

        expect(input).toEqual(result);
    });

    test('правильно формирует строку если json не оборван', () => {
        const input = formatInvalidJsonString(VALID_JSON_STR + INVALID_END, PLAIN_TEXT_MARKER);

        const result = JSON_STR_FROMATTED + INVALID_END;

        expect(input).toEqual(result);
    });

    test('возвращает undefined если начинается не как валидный object или array', () => {
        expect(formatInvalidJsonString('Plain text', PLAIN_TEXT_MARKER)).toBeUndefined();
    });
});
