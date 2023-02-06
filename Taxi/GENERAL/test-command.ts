import {handle as unitHandle, HandleInput as UnitHandleInput} from 'cli/test/unit-command';

type HandleInput = UnitHandleInput;

export async function handle(input: HandleInput = {}) {
    const {pathList, help, ci} = input;

    await unitHandle({pathList, ci, help});
}
