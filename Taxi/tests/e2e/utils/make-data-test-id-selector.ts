/**
 * @function
 * @param selectors
 * @returns
 */
export function makeDataTestIdSelector(selectors: Hermione.GenericSelector) {
    return [selectors]
        .flat()
        .map((genericSelector) => {
            if (typeof genericSelector !== 'string' && 'selector' in genericSelector) {
                return genericSelector.selector;
            }

            const testId = typeof genericSelector === 'string' ? genericSelector : genericSelector.testId;
            const modifier = typeof genericSelector === 'string' ? '' : genericSelector.modifier ?? '';
            return `[data-testid${modifier}='${testId}']`;
        })
        .join(' ');
}
