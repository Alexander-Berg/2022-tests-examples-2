import { wrapLastWordWithSpan } from '../wrapLastWordWithSpan';

describe('wrapLastWordWithSpan', function() {
    const cases = [
        {
            name: 'текст с последним словом',
            text: 'текст с последним словом',
            expected: 'текст с последним <span  class="wrapped">словом<span class=\'icon\'></span></span>'
        },
        {
            name: 'неразрывный пробел у последнего слова',
            text: 'неразрывный пробел у последнего&nbsp;слова',
            expected: 'неразрывный пробел у <span  class="wrapped">последнего&nbsp;слова<span class=\'icon\'></span></span>'
        },
        {
            name: 'текст с переносом',
            text: 'текст с\nпереносом',
            expected: 'текст <span  class="wrapped">с\nпереносом<span class=\'icon\'></span></span>'
        }
    ];

    cases.forEach(testCase => {
        it(testCase.name, function() {
            const result = wrapLastWordWithSpan({
                text: testCase.text,
                node: <span class="icon" />,
                className: 'wrapped'
            });
            expect(result).toEqual(testCase.expected);
        });
    });
});
