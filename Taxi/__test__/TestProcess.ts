import {SlaveProcess} from '../Process';

class TestProcess extends SlaveProcess {
    private _transformer: Function;

    public async init(transformerPath: string) {
        this._transformer = require(transformerPath).default;
        await super.init(transformerPath);
    }

    public run(str: string) {
        return Promise.resolve(this._transformer(str));
    }
}

const [, , ...args] = process.argv;
(new TestProcess(process)).init(args[0]);
