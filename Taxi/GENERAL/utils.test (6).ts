import {decideInitialValues} from './utils';

const donationAmounts = {
    oneshot: {
        amounts: [
            {
                label: '200 ₽',
                value: 200,
            },
            {
                label: '500 ₽',
                value: 500,
            },
            {
                label: '1 000 ₽',
                value: 1000,
            },
            {
                label: '2 000 ₽',
                value: 2000,
            },
            {
                label: '50 000 ₽',
                value: 50000,
            },
        ],
        defaultIndex: 2,
    },
    subs: {
        amounts: [
            {
                label: '200 ₽',
                value: 200,
            },
            {
                label: '500 ₽',
                value: 500,
            },
            {
                label: '1 000 ₽',
                value: 1000,
            },
            {
                label: '2 000 ₽',
                value: 2000,
            },
            {
                label: '5 000 ₽',
                value: 5000,
            },
        ],
        defaultIndex: 4,
    },
};

describe('DonateForm:utils:decideInitiaValue', () => {
    test('правильные умолчания без параметров', () => {
        const initialValues = decideInitialValues({
            donationAmounts,
        });

        expect(initialValues).toEqual({
            recurrent: 'one_time',
            amountIndex: 2,
            manualAmount: '',
            name: '',
            email: '',
            rejectNewsletter: false,
        });
    });

    test('умолчание при некорректном recurrent в урлах', () => {
        const initialValues = decideInitialValues({
            donationAmounts,
            parentQuery: {recurrent: 'incorrect', amount: '500'},
            query: {recurrent: 'wrong', amount: '200'},
        });
    
        expect(initialValues).toEqual({
            recurrent: 'one_time',
            amountIndex: 2,
            manualAmount: '',
            name: '',
            email: '',
            rejectNewsletter: false,
        });
    });

    test('параметры берутся из урла приложения, если в нём определен recurrent, amount мэтчится по списку опций', () => {
        const initialValues = decideInitialValues({
            donationAmounts,
            query: {recurrent: 'one_time', amount: '200'},
        });
    
        expect(initialValues).toEqual({
            recurrent: 'one_time',
            amountIndex: 0,
            manualAmount: '',
            name: '',
            email: '',
            rejectNewsletter: false,
        });
    });

    test('параметры берутся из урла родительского окна, если в нём валидный recurrent, amount мэтчится по списку опций', () => {
        const initialValues = decideInitialValues({
            donationAmounts,
            parentQuery: {recurrent: 'regular', amount: '500'},
            query: {recurrent: 'one_time', amount: '200'},
        });
    
        expect(initialValues).toEqual({
            recurrent: 'regular',
            amountIndex: 1,
            manualAmount: '',
            name: '',
            email: '',
            rejectNewsletter: false,
        });
    });

    test('произвольная сумма из урла выставляется как введённая вручную', () => {
        const initialValues = decideInitialValues({
            donationAmounts,
            query: {recurrent: 'one_time', amount: '12345'},
        });
    
        expect(initialValues).toEqual({
            recurrent: 'one_time',
            amountIndex: 2,
            manualAmount: '12345 ₽',
            name: '',
            email: '',
            rejectNewsletter: false,
        });
    });

    test('невалидная сумма из урла не учитывается', () => {
        const initialValues = decideInitialValues({
            donationAmounts,
            query: {recurrent: 'one_time', amount: '123,45'},
        });
    
        expect(initialValues).toEqual({
            recurrent: 'one_time',
            amountIndex: 2,
            manualAmount: '',
            name: '',
            email: '',
            rejectNewsletter: false,
        });
    });

    test('рекурент для залогина по умолчанию', () => {
        const initialValues = decideInitialValues({
            donationAmounts,
            isUserLoggedIn: true,
        });
    
        expect(initialValues).toHaveProperty('recurrent', 'regular');
    });

    test('единоразовый из урла перекрывает рекурент для залогина по умолчанию', () => {
        const initialValues = decideInitialValues({
            donationAmounts,
            isUserLoggedIn: true,
            query: {recurrent: 'one_time'},
        });
    
        expect(initialValues).toHaveProperty('recurrent', 'one_time');
    });

    test('email и имя передаются без изменений', () => {
        const initialValues = decideInitialValues({
            donationAmounts,
            name: 'Тестовое Имя',
            email: 'test@email.com',
        });
    
        expect(initialValues).toHaveProperty('name', 'Тестовое Имя');
        expect(initialValues).toHaveProperty('email', 'test@email.com');
    });
});
