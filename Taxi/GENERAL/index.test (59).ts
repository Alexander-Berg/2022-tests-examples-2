import {helloB} from './index';

describe('package "tst-b"', () => {
    it('should print greetings', () => {
        console.log('Greetings from "tst-b" package test!');
        helloB();
    });
});
