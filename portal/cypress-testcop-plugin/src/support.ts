function readEnv<T>(variable: string, defaultValue: T, errorMsg: string): T {
    let res;
    try {
        res = JSON.parse(Cypress.env(variable));
    } catch (e) {
        console.error('Cypress Testcop Plugin: ' + errorMsg);
        res = defaultValue;
    }
    return res;
}

/**
 * Support function for skiping and muting tests.
 * Under the hood:
 * Wraps it and describe functions to skip tests.
 * Uses Cypress test:after:run event to mute tests.
 */
export function CypressTestcopSupport() {
    const skipList = readEnv<string[]>('skiplist', [], 'Could not get tests to skip. Using empty list');
    const muteList = readEnv<string[]>('mutelist', [], 'Could not get tests to mute. Using empty list');
    const changedFiles = readEnv<string[]>('changedfiles', [],
        'Cypress Testcop Plugin: Could not get changedFiles. Using empty list');

    const browser = Cypress.env('skipbrowser') || '';
    // prevent multiple registrations
    // https://github.com/cypress-io/cypress-grep/issues/59
    if (it.name === 'itSkip') {
        return;
    }
    // preserve the real "it", "describe" functions
    const _it = it;
    const _describe = describe;
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    it = function itSkip(name, options, callback) {
        if (typeof options === 'function') {
            // the test has format it('...', cb)
            callback = options;
            options = {};
        }

        if (!callback) {
            // the pending test by itself
            return _it(name, options);
        }

        const testName = suiteStack.length > 0 ?
            (suiteStack.join(' ') + ' ' + name + (browser ? ('.' + browser) : '')) :
            name;
        const shouldRun = !skipList.includes(testName);

        if (shouldRun) {
            return _it(name, options, callback);
        }
        return _it.skip(name, options, callback);
    };
    // overwrite "specify" which is an alias to "it"
    specify = it;

    // keep the ".skip", ".only" methods the same as before
    it.skip = _it.skip;
    it.only = _it.only;
    // preserve "it.each" method if found
    // https://github.com/cypress-io/cypress-grep/issues/72
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    if (typeof _it.each === 'function') {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        it.each = _it.each;
    }

    // list of "describe" suites for the current test
    // when we encounter a new suite, we push it to the stack
    // when the "describe" function exits, we pop it
    // Thus a test can look up the tags from its parent suites
    const suiteStack: string[] = [];

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    describe = function describeSkip(name, options, callback) {
        if (typeof options === 'function') {
            // the block has format describe('...', cb)
            callback = options;
            options = {};
        }

        suiteStack.push(name);

        if (!callback) {
            // the pending suite by itself
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            const result = _describe(name, options);
            suiteStack.pop();
            return result;
        }

        const result = _describe(name, options, callback);
        suiteStack.pop();
        return result;
    };
    // overwrite "context" which is an alias to "describe"
    context = describe;

    const getTestNameAndFile = (test: Mocha.Test) => {
        let node: Mocha.Test | Mocha.Suite | undefined = test;
        let stack: string[] = [];
        while (node) {
            stack.push(node.title);
            node = node.parent;
            if (node?.root) {
                break;
            }
        }
        const testName = stack.length > 0 ?
            (stack.reverse().join(' ') + (browser ? ('.' + browser) : '')) : test.title;
        return [testName, node?.file || ''];
    };

    Cypress.on('test:after:run', (attributes, test) => {
        if (attributes.state === 'failed') {
            const [name, file] = getTestNameAndFile(test);
            if (muteList.includes(name) && !(file && changedFiles.some(f => f.includes(file)))) {
                // Test is muted. Still fail in cypress:open
                attributes.state = 'pending';
            }
        }
    });
}
