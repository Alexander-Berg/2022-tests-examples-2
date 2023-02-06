import {parseYaTaxiUserHeader} from '../parseYaTaxiUserHeader'

describe('parseYaTaxiUserHeader', () => {
  test('ignores unlisted params', () => {
    const header = 'unlisted_param=15,eats_user_id=17'
    const data = parseYaTaxiUserHeader(header)
    expect(data['unlisted_param' as keyof typeof data]).not.toBeDefined()
  })

  test('adds listed params to result', () => {
    const header = 'eats_user_id=17,personal_phone_id=19,personal_email_id=65'
    const data = parseYaTaxiUserHeader(header)
    expect(data.eats_user_id).toBe('17')
    expect(data.personal_phone_id).toBe('19')
    expect(data.personal_email_id).toBe('65')
  })

  test('trims values of params', () => {
    const header = 'personal_phone_id= 144  '
    const data = parseYaTaxiUserHeader(header)
    expect(data.personal_phone_id).toBe('144')
  })
})
