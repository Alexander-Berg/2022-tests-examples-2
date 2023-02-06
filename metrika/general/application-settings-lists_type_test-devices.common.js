BEM.JSON.decl({name: 'application-settings-lists', modName: 'type', modVal: 'test-devices'}, {

    onBlock (ctx) {
        var iRbac = BN('i-internal-rbac'),
            appId = (BN('i-params').get('item') || {}).appId;

        if (appId === undefined) {
            return;
        }

        ctx.defer(
            BN('i-internal-rbac').getAppPermissions(appId)
                .then(function (appPermissions) {
                    var hasReadAccess = iRbac.hasPermissions(
                        appPermissions,
                        iRbac.PERMISSION_READ
                    );

                    ctx.param('hasReadAccess', hasReadAccess);
                    ctx.param(
                        'hasWriteAccess',
                        iRbac.hasPermissions(
                            appPermissions,
                            iRbac.PERMISSION_WRITE
                        )
                    );

                    return hasReadAccess ?
                        BN('i-attribution').list(appId) :
                        Vow.reject({status: 403});
                })
                .then(function (data) {
                    ctx.param('data', data.devices);
                })
                .fail(function (err) {
                    if (err && err.status) {
                        if (err.status === 404) {
                            ctx.stop();
                            BN('i-router').missing();
                        }
                        if (err.status === 403 || err.status === 401) {
                            BN('i-response').error({status: 403});
                        }
                    }

                    BN('i-response').error(err);
                })
        );
    },
});
