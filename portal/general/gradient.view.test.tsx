import { execView } from '@lib/views/execView';
import { Gradient } from '@block/gradient/gradient.view';

describe('gradient', function() {
    it('генерирует простой бэкграунд', function() {
        expect(execView(Gradient, '#aba')).toEqual('background-color:#aba;');
        expect(execView(Gradient, 'lime')).toEqual('background-color:lime;');
    });

    it('генерирует градиент с 2 цветами', function() {
        expect(execView(Gradient, '#aba,#beb')).toEqual('background-color:#aba;' +
            'background-image:-webkit-linear-gradient(0deg,#aba 0%,#beb 100%);' +
            'background-image:linear-gradient(90deg,#aba 0%,#beb 100%);');

        expect(execView(Gradient, 'black,white')).toEqual('background-color:black;' +
            'background-image:-webkit-linear-gradient(0deg,black 0%,white 100%);' +
            'background-image:linear-gradient(90deg,black 0%,white 100%);');

        expect(execView(Gradient, '#1a5b8b, #309aad')).toEqual('background-color:#1a5b8b;' +
            'background-image:-webkit-linear-gradient(0deg,#1a5b8b 0%,#309aad 100%);' +
            'background-image:linear-gradient(90deg,#1a5b8b 0%,#309aad 100%);');
    });

    it('генерирует градиент с 3 цветами', function() {
        expect(execView(Gradient, '#aba,#beb, #cac')).toEqual('background-color:#aba;' +
            'background-image:-webkit-linear-gradient(0deg,#aba 0%,#beb 50%,#cac 100%);' +
            'background-image:linear-gradient(90deg,#aba 0%,#beb 50%,#cac 100%);');

        expect(execView(Gradient, 'red,green,blue')).toEqual('background-color:red;' +
            'background-image:-webkit-linear-gradient(0deg,red 0%,green 50%,blue 100%);' +
            'background-image:linear-gradient(90deg,red 0%,green 50%,blue 100%);');

        expect(execView(Gradient, '#1a5b8b, #309aad, #123bcd')).toEqual('background-color:#1a5b8b;' +
            'background-image:-webkit-linear-gradient(0deg,#1a5b8b 0%,#309aad 50%,#123bcd 100%);' +
            'background-image:linear-gradient(90deg,#1a5b8b 0%,#309aad 50%,#123bcd 100%);');
    });

    it('генерирует градиенты с углом', function() {
        expect(execView(Gradient, '#aba,10')).toEqual('background-color:#aba;');

        expect(execView(Gradient, '#1a5b8b, #309aad, 10')).toEqual('background-color:#1a5b8b;' +
            'background-image:-webkit-linear-gradient(80deg,#1a5b8b 0%,#309aad 100%);' +
            'background-image:linear-gradient(10deg,#1a5b8b 0%,#309aad 100%);');

        expect(execView(Gradient, 'red,green,blue,120')).toEqual('background-color:red;' +
            'background-image:-webkit-linear-gradient(330deg,red 0%,green 50%,blue 100%);' +
            'background-image:linear-gradient(120deg,red 0%,green 50%,blue 100%);');

        expect(execView(Gradient, 'red,green,blue,magenta,90')).toEqual('background-color:red;' +
            'background-image:-webkit-linear-gradient(0deg,red 0%,green 33%,blue 66%,magenta 100%);' +
            'background-image:linear-gradient(90deg,red 0%,green 33%,blue 66%,magenta 100%);');
    });

    it('допускает опциональные пробелы', function() {
        expect(execView(Gradient, '#aba, 231')).toEqual('background-color:#aba;');
        expect(execView(Gradient, '#aba ,231')).toEqual('background-color:#aba;');

        expect(execView(Gradient, '#aba, #beb, 120')).toEqual('background-color:#aba;' +
            'background-image:-webkit-linear-gradient(330deg,#aba 0%,#beb 100%);' +
            'background-image:linear-gradient(120deg,#aba 0%,#beb 100%);');

        expect(execView(Gradient, '#aba , #beb , 90')).toEqual('background-color:#aba;' +
            'background-image:-webkit-linear-gradient(0deg,#aba 0%,#beb 100%);' +
            'background-image:linear-gradient(90deg,#aba 0%,#beb 100%);');

        expect(execView(Gradient, '  #aba, #beb, red,  olive  ')).toEqual('background-color:#aba;' +
            'background-image:-webkit-linear-gradient(0deg,#aba 0%,#beb 33%,red 66%,olive 100%);' +
            'background-image:linear-gradient(90deg,#aba 0%,#beb 33%,red 66%,olive 100%);');
    });
});
