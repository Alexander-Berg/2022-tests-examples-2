import * as extracted from '../complete.js';

describe('Complete.Complete', () => {
    describe('getChildContext', () => {
        it('should return object', () => {
            const obj = {
                props: {
                    form: {
                        prefix: 'prefix'
                    }
                }
            };

            expect(extracted.getChildContext.call(obj)).toEqual({
                prefix: obj.props.form.prefix
            });
        });
    });
});
