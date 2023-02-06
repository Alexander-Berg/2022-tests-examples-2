import {SlaveProcess} from '../Process';

class InitFailProcess extends SlaveProcess {
    public init(): Promise<void> {
        throw new Error();
    }

    public run() {
        return Promise.resolve();
    }
}

(new InitFailProcess(process)).init();
