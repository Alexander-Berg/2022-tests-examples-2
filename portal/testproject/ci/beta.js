/* eslint no-console:0 */
const {ci} = require('@yandex-int/tkit'),
    {createWorkflow} = require('urelease/lib/workflow'),
    project = 'testproject',
    version = ci.getCommit() || 'badcommit',
    pr = ci.getPullRequest();
/*
    patches = [
        {
            componentId: 'morda-assessor',
            parentExternalId: 'stable_morda_man_yp',
            resources: [
                {
                    manageType: 'SANDBOX_RESOURCE',
                    localPath: 'portal-morda-front.tar.gz',
                    sandboxResourceType: 'PORTAL_MORDA_FRONT_BETA_TARBALL'
                },
                {
                    manageType: 'SANDBOX_RESOURCE',
                    localPath: 'portal-morda-tmpl.tar.gz',
                    sandboxResourceType: 'PORTAL_MORDA_TMPL_BETA_TARBALL'
                },
                {
                    manageType: 'SANDBOX_RESOURCE',
                    localPath: 'portal-morda-tmpl-skins.tar.gz',
                    sandboxResourceType: 'PORTAL_MORDA_TMPL_SKINS_BETA_TARBALL'
                }
            ]
        }
    ];
*/

if (!pr) {
    console.error(`Нет нужного: ${pr} (${version})`);
    process.exit(1);
}


console.log(`Деплоим: ${pr} (${version})`);

createWorkflow({
    project,
    ref: version,
    version: `pr-${pr}-${version}`,
    instance: `pr-${pr}`
})
    .withTkitParams({
        repo: {},
        resourcesDir: process.env.RESULT_RESOURCES_PATH + '/urelease',
        stopOnUpdate: false
    })
    /*
    .withYappyDeploy({
        templateName: project,
        suffix: `pr-${pr}`,
        readinessTimeout: 40,
        patches: patches
    })
    */
    .justBuildResources({})
    /* деплой в яппи не будет дожидаться завершения заливки в s3,
     * но беты стартуют достаточно медленно, чтобы заливка завершилась.
     */
    .withS3Deploy({
        //noRebuild: true
    })
    .start()
    .then(status => {
        const fail = Object.keys(status.steps)
            .some((key) => status.steps[key].status === 'failure');
        if (fail) {
            throw new Error('Failed!\n' + JSON.stringify(status, null, '  '));
        }
        console.log('Success!\n' + JSON.stringify(status, null, '  '));
    })
    .catch(error => {
        console.log('Workflow failed!', error);
        process.exit(1);
    });
