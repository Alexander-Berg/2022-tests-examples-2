export const translitRusEng = (
  enteredValue = '',
  options?: {slug?: string; engToRus?: boolean; lowerCase?: boolean},
) => {
  const {slug, lowerCase} = options || {}
  const doubleLetters = ['yo', 'zh', 'cz', 'ch', 'sh', 'yu', 'ju', 'ya', 'ja', 'ts', 'kh', 'e`', '``']
  const tripleLetters = ['shh']
  const symbolsTableEng = {} as Record<string, string>
  const symbolsTableRus = {
    а: 'a',
    б: 'b',
    в: 'v',
    г: 'g',
    д: 'd',
    е: 'e',
    ё: 'yo',
    ж: 'zh',
    з: 'z',
    и: 'i',
    й: 'j',
    к: 'k',
    л: 'l',
    м: 'm',
    н: 'n',
    о: 'o',
    п: 'p',
    р: 'r',
    с: 's',
    т: 't',
    у: 'u',
    ф: 'f',
    х: 'h',
    ц: 'cz',
    ч: 'ch',
    ш: 'sh',
    щ: 'shh',
    ъ: slug ? '' : '``',
    ы: 'y',
    ь: slug ? '' : '`',
    э: slug ? 'e' : 'e`',
    ю: 'yu',
    я: 'ya',
  } as Record<string, string>

  for (const key in symbolsTableRus) {
    if (symbolsTableRus[key]) {
      symbolsTableEng[symbolsTableRus[key]] = key
    }
  }
  symbolsTableEng['c'] = 'ц'
  symbolsTableEng['ts'] = 'ц'
  symbolsTableEng['ja'] = 'я'
  symbolsTableEng['ju'] = 'ю'
  symbolsTableEng['kh'] = 'х'

  const convertLetters = function (enteredValue: string) {
    const lettersReady: Array<string> = []
    const lettersEdited: Array<string> = []

    const enteredValueArr = lowerCase ? enteredValue.toLowerCase().split('') : enteredValue.split('')

    enteredValueArr.forEach(function (letter, index) {
      if (index > 0 && doubleLetters.indexOf(enteredValue[index - 1] + enteredValue[index]) !== -1) {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        lettersReady[index - 1] = false
        lettersReady[index] = enteredValue[index - 1] + enteredValue[index]
      } else if (
        index > 1 &&
        tripleLetters.indexOf(enteredValue[index - 2] + enteredValue[index - 1] + enteredValue[index]) !== -1
      ) {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        lettersReady[index - 1] = lettersReady[index - 2] = false
        lettersReady[index] = enteredValue[index - 2] + enteredValue[index - 1] + enteredValue[index]
      } else {
        lettersReady.push(letter)
      }
    })

    lettersReady.map(function (letter) {
      const capitalizeLetter = (str: string) => str.charAt(0).toUpperCase() + str.slice(1)
      if (letter) {
        const isUpperCase = letter !== '`' && letter !== '``' && letter === letter.toUpperCase()
        const loweredLetter = letter.toLowerCase()
        if (symbolsTableRus[loweredLetter] !== undefined) {
          const resultingLetter = isUpperCase
            ? capitalizeLetter(symbolsTableRus[loweredLetter])
            : symbolsTableRus[loweredLetter]
          lettersEdited.push(resultingLetter)
        } else if (loweredLetter === ' ' && slug) {
          lettersEdited.push('_')
        } else {
          lettersEdited.push(letter)
        }
      }
    })

    return lettersEdited
  }

  return convertLetters(enteredValue).join('')
}
