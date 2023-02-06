import {SlaveProcess} from '../Process';

class RunFailProcess extends SlaveProcess {
    public run(): Promise<void> {
        throw new Error();
    }
}

(new RunFailProcess(process)).init();
