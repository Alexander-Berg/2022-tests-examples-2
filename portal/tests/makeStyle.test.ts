import { makeStyle } from '../makeStyle';

describe('home.makeStyle', function() {
    test('should render nothing on empty', function() {
        expect(makeStyle({})).toEqual('');
    });

    test('should render style', function() {
        expect(makeStyle({
            width: '10px'
        })).toEqual('width:10px');

        expect(makeStyle({
            width: '10px',
            height: '20px'
        })).toEqual('width:10px;height:20px');

        expect(makeStyle({
            width: '10px',
            height: '20px',
            margin: undefined
        })).toEqual('width:10px;height:20px');

        expect(makeStyle({
            width: '10px',
            height: '20px',
            margin: 0
        })).toEqual('width:10px;height:20px;margin:0');
    });
});
