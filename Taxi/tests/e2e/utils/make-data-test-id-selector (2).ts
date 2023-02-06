/**
 * @function
 * @description Строит селектор вида `"[data-testid='foo'] [data-testid='bar'] ..."`
 * Поддерживает операторы ^, $, * для построения селектора, если селектор начинается `\\`,
 * то будет использован "как есть", без приведения к виду [data-testid='...']
 * @param selectors
 * @returns
 */
export default function makeDataTestIdSelector(selectors: Hermione.Selector) {
    return [selectors]
        .flat()
        .map((testId) => {
            let value = testId;
            if (value.startsWith('\\')) {
                return value.replace('\\', '');
            }
            let operator = '=';
            const firstChar = testId[0];
            if (['^', '$', '*'].includes(firstChar)) {
                operator = firstChar + operator;
                value = value.substring(1);
            }
            return `[data-testid${operator}'${value}']`;
        })
        .join(' ');
}
