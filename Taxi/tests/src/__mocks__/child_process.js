const child_process = jest.genMockFromModule('child_process');

const mockOutput = new Map()

const defaultArgsFactory = (command) => [
    undefined,
    command,
    ''
];

const exec = jest.fn().mockImplementation((command, commandOptions, cb) => {
    const argsFactory = mockOutput.get(command) || defaultArgsFactory

    cb(...argsFactory(command, commandOptions))

    return {
        stdout: () => {},
        stderr: () => {}
    }
})

const __setResponse = (command, argsFactory) => {
    mockOutput.set(command, argsFactory);
}

child_process.exec = exec
child_process.__setResponse = __setResponse;

module.exports = child_process;