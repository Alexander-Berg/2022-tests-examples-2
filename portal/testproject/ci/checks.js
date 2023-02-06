/* eslint no-console:0 */
const {
    Graph,
    ci
} = require('@yandex-int/tkit');

const isPullRequest = ci.getEvent() === 'pull_request';

console.log(`run checks
is PR: ${isPullRequest},
cwd is: ${process.cwd()},
config: ${process.env.checkout_config}
`);

(async function () {

    const graph = new Graph({
        repo: {},
        subscribers: ['core'],
        failOnStepFailure: false,
        selective: true,
        hideIntermediate: true,
        stopOnUpdate: false
    });

    const treeConfig = {
        reported: null,
        changed: null,
        succeed: ['changed']
    };

    const steps = {
        changed: [
            'echo "changed files"  %s',
            {
                files: ['**'],
                partialRun: true
            }
        ],
        reported: [
            'mkdir report && echo \'<h1>hello</h1>\' > report/index.html',
            {
                report: 'report',
                main: 'index.html',
                type: 'html'
            }
        ],
        succeed: 'echo "yay"; exit 0'
    };

    return graph.run(treeConfig, steps);
})()
    .catch((err) => {
        console.error(err);
        process.exit(1);
    });

