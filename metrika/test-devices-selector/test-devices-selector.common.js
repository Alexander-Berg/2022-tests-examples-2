/**
 * @prop {Number} appId
 * @prop {String} purpose
 */
BEM.JSON.decl('test-devices-selector', {

    onBlock (ctx) {
        var params = ctx.params();

        ctx.defer(
            BN('i-attribution').list(params.appId, params.purpose)
                .then(function (res) {
                    ctx.param('list', res.devices || []);
                })
        );
    },

});
