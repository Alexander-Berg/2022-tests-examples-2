import { castBooleanStringDeep } from 'server/utils/cast-boolean-string-deep'

interface Case {
  input: unknown
  output: unknown
}

const cases: Case[] = [
  {
    input: 'true',
    output: true,
  },
  {
    input: 'false',
    output: false,
  },
  {
    input: 'True',
    output: 'True',
  },
  {
    input: 'False',
    output: 'False',
  },
  {
    input: 'string',
    output: 'string',
  },
  {
    input: 123,
    output: 123,
  },
  {
    input: [
      'false',
      123,
      'string',
      {
        key1: 'true',
        key2: {
          subkey1: 123,
          subkey2: 'string',
        },
        key3: null,
        key4: ['string', 'true', 'false'],
        key5: undefined,
      },
      'true',
    ],
    output: [
      false,
      123,
      'string',
      {
        key1: true,
        key2: {
          subkey1: 123,
          subkey2: 'string',
        },
        key3: null,
        key4: ['string', true, false],
        key5: undefined,
      },
      true,
    ],
  },
  {
    input: {
      key1: 'true',
      key2: {
        subkey1: 123,
        subkey2: 'string',
      },
      key3: null,
      key4: ['string', 'true', 'false'],
      key5: undefined,
    },
    output: {
      key1: true,
      key2: {
        subkey1: 123,
        subkey2: 'string',
      },
      key3: null,
      key4: ['string', true, false],
      key5: undefined,
    },
  },
]

describe('cast boolean string deep', () => {
  test.each(cases)('Cast $input', ({ input, output }) => {
    const actual = castBooleanStringDeep(input)
    expect(actual).toEqual(output)
  })
})
