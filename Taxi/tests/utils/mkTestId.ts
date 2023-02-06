const makeDataTestId = (value: string) => {
  return `[data-testid="${value}"]`
}

const makeDataId = (value: string) => {
  return `[data-id="${value}"]`
}

/* Создаёт [data-testid="value"] аттрибут. Короткое название из-за частоты использования. */
export const mkTestId = (querySelector: string) => {
  const data = querySelector.split(' ')
  if (data.length > 1) {
    return data.map(makeDataTestId).join(' ')
  }
  return makeDataTestId(querySelector)
}

/* Создаёт [data-id="value"] аттрибут. Короткое название из-за частоты использования. */
export const mkDataId = (querySelector: string) => {
  const data = querySelector.split(' ')
  if (data.length > 1) {
    return data.map(makeDataId).join(' ')
  }
  return makeDataId(querySelector)
}
