import OriginalEmitter from 'events';

import { isPatched, patch, unpatch } from '..';

type EmitParameters = Parameters<typeof OriginalEmitter.prototype.emit>;
type EmitReturn = ReturnType<typeof OriginalEmitter.prototype.emit>;
type OnParameters = Parameters<typeof OriginalEmitter.prototype.on>;

/**
 * Будем тестировать манки-патчинг на классе EventEmitter, на методах .on и .emit
 * Т.к. EventEmitter широко используется в ноде, а тесты теоретически могут запускаться параллельно
 * то чтобы чего-нибудь не сломать, делаем его наследника BaseEventEmitter (проверять прототип) и EventEmitter (проверять методы инстанса)
 */
class BaseEventEmitter extends OriginalEmitter {
    emit(...args: EmitParameters): EmitReturn {
        return super.emit(...args);
    }

    // не осилил, как обойтись без `: any`
    on(...args: OnParameters): any {
        return super.emit(...args);
    }
}

class EventEmitter extends BaseEventEmitter {}

describe('monkey-patch', () => {
    describe('patch', () => {
        it('instance methods', () => {
            const emitter = new EventEmitter();
            const handler = jest.fn();
            patch(emitter, 'emit', (original, ...args) => {
                handler();
                return original.call(this, ...args);
            });
            expect(handler).toHaveBeenCalledTimes(0);
            emitter.emit('test', 'any data');
            expect(handler).toHaveBeenCalledTimes(1);
        });
        it('prototype methods', () => {
            const handler = jest.fn();
            const args1: EmitParameters = [
                'test1',
                'any data1',
                'one more data1',
            ];
            const args2: EmitParameters = [
                'test2',
                'any data2',
                'one more data2',
            ];
            patch(EventEmitter.prototype, 'emit', (original, ...args) => {
                handler(...args);
                return original.call(this, ...args);
            });
            const emitter1 = new EventEmitter();
            const emitter2 = new EventEmitter();

            expect(handler).toHaveBeenCalledTimes(0);
            emitter1.emit(...args1);
            expect(handler).toHaveBeenCalledTimes(1);
            expect(handler).toHaveBeenCalledWith(...args1);
            emitter2.emit(...args2);
            expect(handler).toHaveBeenCalledTimes(2);
            expect(handler).toHaveBeenCalledWith(...args2);
            unpatch(EventEmitter.prototype.emit);
        });
        it('with proper arguments', () => {
            const emitter = new EventEmitter();
            const handler = jest.fn();
            const args: EmitParameters = ['test', 'any data', 'one more dara'];
            let original: any;
            patch(emitter, 'emit', (passedOriginal, ...args) => {
                original = passedOriginal;
                handler(...args);
                return passedOriginal.call(this, ...args);
            });
            emitter.emit(...args);

            expect(original).toBe(EventEmitter.prototype.emit);
            expect(handler).toBeCalledWith(...args);
        });
    });
    describe('isPatched', () => {
        it('works', () => {
            const emitter = new EventEmitter();
            expect(isPatched(emitter.on)).toBe(false);

            patch(emitter, 'on', (original, ...args) => {
                return original.call(this, ...args);
            });

            expect(isPatched(emitter.on)).toBe(true);
        });
    });
    describe('unpatch', () => {
        it('works', () => {
            const emitter = new EventEmitter();
            expect(isPatched(emitter.on)).toBe(false);

            patch(emitter, 'on', (original, ...args) => {
                return original.call(this, ...args);
            });
            expect(isPatched(emitter.on)).toBe(true);

            unpatch(emitter.on);
            expect(isPatched(emitter.on)).toBe(false);
        });
    });
});
