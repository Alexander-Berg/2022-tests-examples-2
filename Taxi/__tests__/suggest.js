const {hlString} = require('../suggest');

describe('suggest', () => {
    it('Should not be found language', () => {
        expect(
            hlString({
                text: 'улица Ленина, 36',
                hl: [
                    [0, 5],
                    [6, 12]
                ]
            })
        ).toEqual([{text: 'улица', type: 'hl'}, {text: ' '}, {text: 'Ленина', type: 'hl'}, {text: ', 36'}]);
    });
});
