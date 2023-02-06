export const makeNthBySelector = (selector: string, nth: number) => {
  return `${selector}:nth-child(${nth})`
}
