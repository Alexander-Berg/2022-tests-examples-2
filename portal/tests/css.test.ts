import { css } from '../css';

describe('home.CSS', function() {
    let cssPart = css();

    test('generates css', function() {
        cssPart.clear();
        cssPart.decl('.first').push('color:red', 'height:20px', 'width:30px');

        expect(cssPart.get()).toEqual('.first{color:red;height:20px;width:30px}');

        cssPart.decl('.second').push('background-color: whitesmoke');

        expect(cssPart.get('.second')).toEqual('.second{background-color: whitesmoke}');
        expect(cssPart.get()).toEqual('.first{color:red;height:20px;width:30px}.second{background-color: whitesmoke}');

        cssPart.decl('.first').push('font-size:14px');

        expect(cssPart.get('.first')).toEqual('.first{color:red;height:20px;width:30px;font-size:14px}');
        expect(cssPart.get()).toEqual('.first{color:red;height:20px;width:30px;font-size:14px}.second{background-color: whitesmoke}');

        cssPart.clear('.first');
        expect(cssPart.get('.second')).toEqual('.second{background-color: whitesmoke}');
        expect(cssPart.get()).toEqual('.second{background-color: whitesmoke}');
    });
});
