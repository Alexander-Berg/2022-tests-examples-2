const execSync = require('child_process').execSync;

// masters/<service_name> -> DEPLOY_BRANCH === <service_name>
const SERVICE_NAME = process.env.BUILD_BRANCH;

(function () {
    execSync(
        `cd services/${SERVICE_NAME} && /opt/nodejs/10/bin/npm run test`,
        {stdio: 'inherit'},
    );
})();
