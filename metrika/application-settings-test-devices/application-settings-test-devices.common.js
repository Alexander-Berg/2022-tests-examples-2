/**
 * Block that provides description and list to add test devices for attribution or push notifications
 */
/**
 * @prop {AttributionPurpose} purpose
 */
BEM.JSON.decl('application-settings-test-devices', {

    onBlock (ctx) {
        ctx.js(true).content([
            {
                elem: 'title',
                content: ctx.i18n('title'),
            },
            {
                elem: 'description',
                content: ctx.i18n('description'),
            },
            {
                elem: 'instruction',
                item: 'how-get-appmetrica',
                steps: 4,
            },
            {
                elem: 'instruction',
                item: 'how-get-google',
                steps: 4,
            },
            {
                elem: 'instruction',
                item: 'how-get-apple',
                steps: 4,
            },
            {
                elem: 'instruction',
                item: 'how-get-idfv',
                steps: 3,
            },
            {
                elem: 'instruction',
                item: 'how-get-windows',
                steps: 2,
            },
            {
                elem: 'instruction',
                item: 'how-get-huawei',
                steps: 2,
            },
            {
                elem: 'devices-list',
                content: {
                    block: 'application-settings-lists',
                    mods: {
                        type: 'test-devices',
                    },
                },
            },
        ]);
    },

    onElem: {
        'instruction' (ctx) {
            var {item, steps} = ctx.params();

            ctx.elemMods({name: item}).content([
                {
                    block: 'link',
                    mix: {
                        block: ctx.getName(),
                        elem: 'instruction-header',
                        js: {name: item},
                    },
                    content: [
                        {
                            elem: 'inner',
                            content: ctx.i18n(item),
                        },
                        {
                            block: 'icon',
                            elem: 'arrow-small',
                            mix: [
                                {
                                    block: ctx.getName(),
                                    elem: 'instruction-header-icon',
                                },
                            ],
                        },
                    ],
                },
                {
                    elem: 'instruction-body',
                    item,
                    steps,
                },
            ]);
        },

        'instruction-body' (ctx) {
            const {item, steps} = ctx.params();
            let stepsList = [];

            for (let i = 1; i <= steps; i++) {
                stepsList.push({
                    tag: 'li',
                    content: {
                        html: ctx.i18n(`${item}-desc-${i}`),
                    },
                });
            }

            ctx.content({
                elem: 'instruction-steps',
                tag: 'ol',
                content: stepsList,
            });
        },
    },
});
