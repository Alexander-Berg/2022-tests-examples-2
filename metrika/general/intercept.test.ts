import { createChain } from './';

function getData() {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({ a: 1 });
        }, 500);
    });
}

describe('intercept', () => {
    it('works', () => {
        const instance = {
            fetchData(spy: jest.Mock<{}>) {
                const chain = createChain(this);

                return getData().then(chain(spy));
            },
        };
        const spy1: jest.Mock<{}> = jest.fn();
        const spy2: jest.Mock<{}> = jest.fn();

        return Promise.all([
            instance.fetchData(spy1),
            instance.fetchData(spy2),
        ]).then(() => {
            expect(spy1).toHaveBeenCalledTimes(0);
            expect(spy2).toHaveBeenCalledTimes(1);
        });
    });
    it('supports multiple parallel calls', () => {
        const instance = {
            fetchData(spy: jest.Mock<{}>) {
                const chain = createChain(this, 'fetchData');

                return getData().then(chain(spy));
            },
            writeData(spy: jest.Mock<{}>) {
                const chain = createChain(this, 'writeData');

                return getData().then(chain(spy));
            },
        };
        const spyFetch1: jest.Mock<{}> = jest.fn();
        const spyFetch2: jest.Mock<{}> = jest.fn();
        const spyWrite1: jest.Mock<{}> = jest.fn();
        const spyWrite2: jest.Mock<{}> = jest.fn();

        return Promise.all([
            instance.fetchData(spyFetch1),
            instance.fetchData(spyFetch2),
            instance.writeData(spyWrite1),
            instance.writeData(spyWrite2),
        ]).then(() => {
            expect(spyFetch1).toHaveBeenCalledTimes(0);
            expect(spyFetch2).toHaveBeenCalledTimes(1);

            expect(spyWrite1).toHaveBeenCalledTimes(0);
            expect(spyWrite2).toHaveBeenCalledTimes(1);
        });
    });
});
