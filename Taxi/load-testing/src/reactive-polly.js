/*
  Расширяем непубличные свойства, поэтому TS только мешает...
 */

import {Polly} from '@pollyjs/core';

export class ReactivePolly extends Polly {
    constructor(...args) {
        super(...args);

        this._requests.push = () => {
            /**
             * "requests over the lifetime of the polly instance"
             * В исходном коде сюда пишутся все перехваченные запросы
             * (инициализируется в конструкторе)
             * Заменяем пустышкой, чтобы не забивать память
             */
        };
    }
}
