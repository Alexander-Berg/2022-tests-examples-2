BEM.JSON.decl('push-campaign-edit-platform', {
    onElem: {
        /**
         * @param {String} platform
         * @param {BEM.Model} model m-push-campaign
         */
        'test-control' (ctx) {
            const block = ctx.getName();
            const {model, platform} = ctx.params();

            ctx.content([
                {
                    block: 'test-devices-selector',
                    mods: {'update-on-event': 'yes'},
                    mix: [{block, elem: 'devices-selector'}],
                    appId: model.get('appId'),
                    purpose: 'push_notifications',
                    platform,
                },
                {
                    elem: 'test-controls-row',
                    content: [
                        {
                            elem: 'button-spin-wrap',
                            content: [
                                {
                                    block: 'button',
                                    mods: {
                                        size: 's',
                                        theme: 'normal',
                                        disabled: 'yes',
                                    },
                                    mix: [
                                        {block, elem: 'test-this-push'},
                                    ],
                                    content: ctx.i18n('test-this-text'),
                                },
                                {
                                    block: 'spin2',
                                    mods: {
                                        size: 'xxs',
                                        progress: 'yes',
                                    },
                                    mix: [
                                        {block, elem: 'test-spin'},
                                    ],
                                },
                            ],
                        },
                    ],
                },
                {
                    elem: 'test-device-label',
                },
            ]);
        },
    },
});
