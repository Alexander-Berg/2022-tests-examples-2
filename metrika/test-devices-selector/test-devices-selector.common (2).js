/**
 * @prop {Number} appId
 * @prop {AttributionPurpose} purpose
 * @prop {Array} list
 * @prop {String} [platform]
 */
BEM.JSON.decl('test-devices-selector', {

    onBlock (ctx) {
        var params = ctx.params(),
            list = BN('test-devices-selector').filterList(params.list, params.platform);

        ctx
            .js(_.pick(params, ['appId', 'purpose', 'platform']))
            .mods({
                empty: list.length ? '' : 'yes',
            })
            .content([
                {elem: 'empty-message'},
                {elem: 'body', list},
            ]);
    },

    onElem: {

        'empty-message' (ctx) {
            ctx.content({
                html: ctx.i18n('empty-text'),
            });
        },

        'body' (ctx) {
            const {
                list = [],
            } = ctx.params();

            ctx.content([
                {
                    block: 'select2',
                    js: {
                        optionsMaxHeight: 288,
                    },
                    mods: {
                        size: 's',
                        width: 'max',
                        text: 'vary',
                        type: 'radio',
                        theme: 'normal',
                    },
                    text: ctx.i18n('try-it'),
                    items: list.map(({ id, name }) => ({
                        val: id,
                        text: name,
                    })),
                },
                {
                    block: 'link',
                    mods: {
                        pseudo: 'yes',
                    },
                    mix: [
                        {
                            block: ctx.getName(),
                            elem: 'add-link',
                        },
                    ],
                    content: ctx.i18n('one-more'),
                },
            ]);
        },

        /**
         * @prop {String} platform
         * @prop {Number} appId
         */
        'popup' (ctx) {
            var params = ctx.params();

            ctx.wrap([{
                block: 'popup',
                mods: {
                    type: 'modal',
                    autoclosable: 'no',
                    position: 'fixed',
                    animate: 'no',
                    padding: 'no',
                },
                mix: [{
                    block: ctx.getName(),
                    elem: 'popup',
                }],
                underMods: {type: 'paranja'},
                content: [
                    {
                        elem: 'content',
                        mix: [{block: ctx.getName(), elem: 'popup-content'}],
                        content: {
                            block: ctx.getName(),
                            elem: 'popup-inner',
                            content: [
                                {
                                    elem: 'modal-header',
                                    appId: params.appId,
                                },
                                {
                                    elem: 'modal-body',
                                    platform: params.platform,
                                },
                                {elem: 'modal-controls'},
                            ],
                        },
                    },
                ],
            }]);
        },

        'modal-header' (ctx) {
            ctx.content([
                {
                    elem: 'main-header',
                    content: ctx.i18n('test-devices'),
                },
                {
                    elem: 'subheader',
                    content: {
                        html: ctx.i18n('subheader', {
                            link: BN('i-url').buildUrl({
                                page: 'i-page-app-edit',
                                type: 'test-devices',
                            }, ['requestedUid', 'item']),
                        }),
                    },
                },
            ]);
        },

        'modal-body' (ctx) {
            var platform = ctx.params().platform;

            ctx.content(['name', 'id', 'type'].map(function (rowName) {
                return {
                    elem: rowName + '-row',
                    mix: [{elem: 'row'}],
                    content: [
                        {
                            elem: rowName + '-first-cell',
                            mix: [{elem: 'cell'}, {elem: 'first-cell'}],
                            content: {
                                elem: 'first-cell-inner',
                                content: ctx.i18n(rowName + '-text'),
                            },
                        },
                        {
                            elem: rowName + '-last-cell',
                            mix: [{elem: 'cell'}, {elem: 'last-cell'}],
                            platform,
                        },
                    ],
                };
            }));
        },

        'name-last-cell' (ctx) {
            ctx.content({
                block: 'input',
                mods: {
                    theme: 'normal',
                    size: 's',
                },
                mix: [
                    {block: ctx.getName(), elem: 'name-input'},
                ],
                content: {
                    elem: 'control',
                },
            });
        },


        'id-last-cell' (ctx) {
            ctx.content({
                block: 'input',
                mods: {
                    theme: 'normal',
                    size: 's',
                },
                mix: [
                    {block: ctx.getName(), elem: 'id-input'},
                ],
                content: {
                    elem: 'control',
                },
            });
        },

        'type-last-cell' (ctx) {
            const platform = ctx.params().platform;
            let attributionByPlatform = BN('i-platform').getAttribution(platform);
            if (_.isArray(attributionByPlatform)) {
                attributionByPlatform = attributionByPlatform[0];
            }

            ctx.content({
                block: 'select',
                mix: [
                    {block: ctx.getName(), elem: 'attribution-select'},
                ],
                mods: {
                    size: 's',
                    theme: 'normal',
                    layout: 'fixed',
                    width: 'auto',
                },
                content: [
                    {
                        block: 'button',
                        type: 'button',
                        mods: {size: 's', theme: 'normal'},
                        content: ctx.i18n(attributionByPlatform + '-name'),
                    },
                    {
                        elem: 'control',
                        content: BN('i-platform').getAttributionsList().map((attribution) => ({
                            elem: 'option',
                            attrs: {
                                selected: attributionByPlatform === attribution && 'selected',
                                value: attribution,
                            },
                            content: ctx.i18n(attribution + '-name'),
                        })),
                    },
                ],
            });
        },

        'modal-controls' (ctx) {
            ctx.content([
                {
                    block: 'button',
                    mods: {
                        size: 's',
                        theme: 'action',
                        disabled: 'yes',
                    },
                    mix: [{block: ctx.getName(), elem: 'save'}],
                    content: ctx.i18n('add'),
                },
                {
                    block: 'button',
                    mods: {
                        size: 's',
                    },
                    mix: [{block: ctx.getName(), elem: 'cancel'}],
                    content: ctx.i18n('cancel'),
                },
            ]);
        },

    },

});

(BEM.DOM || BEM).decl('test-devices-selector', null, {

    filterList (list, platform) {
        var attribution = BN('i-platform').getAttribution(platform);

        if (!attribution) {
            return list;
        }

        return list.filter(({type}) =>
            _.isArray(attribution) ?
                attribution.includes(type) :
                type === attribution,
        );
    },

});
