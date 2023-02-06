import {snakefy, changePropertyCasing, snakefyDeep} from './object'

describe('snakefy - преобразование объекта в snakeCase', () => {
  test('', () => {
    const data = snakefy({
      testData: 123,
    })
    expect(data.test_data).toBeDefined()
  })
  test('null не должен быть undefined', () => {
    const data = snakefy({
      testData: null,
    })
    expect(data.test_data).toBeDefined()
  })
  test('Объект должен заменяться по всей глубине', () => {
    const data = snakefyDeep({
      data: {
        testCase: {
          caseOne: 1,
          caseNull: null,
        },
      },
    })
    expect(data.data.test_case.case_one).toEqual(1)
    expect(data.data.test_case.case_null).toBeNull()
  })
  test('Значения массива должны оставаться как есть', () => {
    const data = snakefy({
      arr: ['testData'],
    })
    expect(data.arr[0]).toEqual('testData')
  })
  test('changePropertyNaming (depth=0 by default)', () => {
    const input = {
      myProperty: {
        subProperty: 1,
      },
    }

    const spy = jest.fn((str: string) => str)

    changePropertyCasing(input, spy)

    expect(spy.mock.calls).toEqual([['myProperty']])
  })

  test('changePropertyNaming (depth=2 goes two levels deep)', () => {
    const input = {
      myProperty: {
        myPropertySub1: {
          myPropertySub2: {
            myPropertySub3: 1,
          },
        },
      },
      arrayPropertyNumber: [1, 2],
      arrayPropertyObject: [
        {
          arraySub: 1,
          arraySubArray: [
            {
              arraySubArraySub: 1,
            },
          ],
        },
      ],
    }

    const spy = jest.fn((str: string) => str)

    changePropertyCasing(input, spy, 2)

    expect(spy.mock.calls).toEqual([
      ['myProperty'],
      ['myPropertySub1'],
      ['myPropertySub2'],
      ['arrayPropertyNumber'],
      ['arrayPropertyObject'],
      ['arraySub'],
      ['arraySubArray'],
    ])
  })

  test('structure check', () => {
    const position = {
      location: [1],
      placeId: '1',
      floor: '1',
      flat: '1',
      doorcode: '1',
      doorcodeExtra: '1',
      entrance: '1',
      buildingName: '1',
      doorbellName: '1',
      leftAtDoor: true,
      meetOutside: true,
      noDoorCall: true,
      postalCode: true,
      comment: true,
    }
    const expectResult = {
      location: [1],
      place_id: '1',
      floor: '1',
      flat: '1',
      doorcode: '1',
      doorcode_extra: '1',
      entrance: '1',
      building_name: '1',
      doorbell_name: '1',
      left_at_door: true,
      meet_outside: true,
      no_door_call: true,
      postal_code: true,
      comment: true,
    }
    const result = snakefy(position, true, 5)
    expect(expectResult).toStrictEqual(result)
  })
})
