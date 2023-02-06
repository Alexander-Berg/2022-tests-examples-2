import chai from 'chai';
import * as sinon from 'sinon';
import * as utils from '@src/providers/ecommerceParser/utils';
import { huffmanEncoder, MAX_MESSAGE_LENGTH, totalsEncoder } from '../encoder';
import { CurrencyId } from '../currencyParser';

type TotalsEncoderTestData = {
    price: number;
    currency: CurrencyId;
    test: string;
};

type HuffmanEncoderTestData = {
    input: Parameters<typeof huffmanEncoder>[1];
    test: string;
};

const totalsTestData: TotalsEncoderTestData[] = [
    {
        price: 0,
        currency: '000',
        test: '25roz25s3',
    },
    {
        price: 1,
        currency: '000',
        test: '25roz6pd0s',
    },
    {
        price: 0,
        currency: '643',
        test: '25roz2dyt',
    },
    {
        price: 1,
        currency: '643',
        test: '25roz6ntci',
    },
    {
        price: 1238.81,
        currency: '643',
        test: '25swz1nolsr',
    },
    {
        price: 118000,
        currency: '643',
        test: '1wtyz2dyt',
    },
    {
        price: 272990.12,
        currency: '643',
        test: '1ihvzroqf',
    },
    {
        price: 1000.7,
        currency: '643',
        test: '25shz4myn1',
    },
];

const huffmanTestDataShortArrays: HuffmanEncoderTestData[] = [
    {
        input: [],
        test: 'AgAAAnTn',
    },
    {
        input: [[], [], []],
        test: 'AgAACnTpyrpyrpy5',
    },
    {
        input: [[200], [], []],
        test: 'AgAADXTp3O9u9uVdOVdOXP8=',
    },
    {
        input: [[], [1], []],
        test: 'AgAAC3TpyrrXrlXTlz8=',
    },
    {
        input: [[], [], ['товар']],
        test: 'AgAAFnTpyrpyrqO1rzlv/mW/Hcs7Z2nYY5c/',
    },
    {
        input: [[200], [1], []],
        test: 'AgAADnTp3O9u9uVda9cq6cuf',
    },
    {
        input: [[], [1], ['milk']],
        test: 'AgAAEXTpyrrXrlXUufXfHLk=',
    },
    {
        input: [[200], [], ['►']],
        test: 'AgAAEnTp3O9u9uVdOVdSz0S7GNvx8cuf',
    },
];

describe('ecommerceParser', () => {
    const sandbox = sinon.createSandbox();
    const randomNumber = '22';
    const win = { JSON, Math } as Window;

    beforeEach(() => {
        sandbox
            .stub(utils, 'generateRandomTwoDigitNumber')
            .returns(randomNumber);
    });
    afterEach(() => {
        sandbox.restore();
    });

    describe('totalsEncoder', () => {
        totalsTestData.forEach(({ price, currency, test }) => {
            it(`encode price:${price}, currency:${currency} to ${test}`, () => {
                chai.expect(totalsEncoder(win, price, currency)).to.be.equal(
                    test,
                );
            });
        });
    });

    describe('HuffmanEncoder', () => {
        huffmanTestDataShortArrays.forEach(({ input, test }) => {
            it(`encode [${JSON.stringify(input)}] to "${test}"`, () => {
                chai.expect(huffmanEncoder(win, input)).to.be.equal(test);
            });
        });

        it(`encode too large an array to ""`, () => {
            const shortInput = [
                [200],
                [1],
                ['a'.repeat(MAX_MESSAGE_LENGTH - 16)],
            ];
            chai.expect(huffmanEncoder(win, shortInput).length).to.be.above(16);

            const longInput = [
                [200],
                [1],
                ['a'.repeat(MAX_MESSAGE_LENGTH - 15)],
            ];
            chai.expect(huffmanEncoder(win, longInput)).to.be.equal('');
        });
    });
});
