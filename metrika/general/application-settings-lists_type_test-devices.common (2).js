BEM.JSON.decl({name: 'application-settings-lists', modName: 'type', modVal: 'test-devices'}, {

    onBlock (ctx) {
        ctx.param('cellDecls', BN(ctx.getName())._TEST_DEVICES_CELL_DECLS);
    },

    onElem: {
        'row' (ctx) {
            ctx.param('cellDecls', BN(ctx.getName())._TEST_DEVICES_CELL_DECLS);
        },

        /**
         * @prop {string} name
         * @prop {boolean} hasWriteAccess
         */
        'name' (ctx) {
            const {
                name,
                hasWriteAccess,
            } = ctx.params();

            const content = {
                block: 'input',
                value: name,
                name: 'name',
                mods: {
                    theme: 'normal',
                    size: 's',
                    disabled: !hasWriteAccess ? 'yes' : '',
                },
                content: {
                    elem: 'control',
                },
            };

            BN(ctx.getName())._setContent(ctx, !hasWriteAccess, content, name);
        },

        /**
         * @prop {string} device_id
         * @prop {boolean} hasWriteAccess
         */
        'device-id' (ctx) {
            const {
                device_id,
                hasWriteAccess,
            } = ctx.params();

            if (!hasWriteAccess) {
                ctx.content(device_id);
                return;
            }

            const content = {
                block: 'input',
                value: device_id,
                name: 'device_id',
                mods: {
                    theme: 'normal',
                    size: 's',
                    disabled: !hasWriteAccess ? 'yes' : '',
                },
                content: {
                    elem: 'control',
                },
            };

            BN(ctx.getName())._setContent(ctx, !hasWriteAccess, content, device_id);
        },

        /**
         * @prop {string} type
         * @prop {boolean} hasWriteAccess
         */
        'type' (ctx) {
            const block = ctx.getName();
            const bemBlock = BN(block);
            const {
                type = bemBlock._DEFAULT_ID_TYPE,
                hasWriteAccess,
            } = ctx.params();

            const content = {
                block: 'select2',
                control: true,
                name: 'type',
                mods: {
                    size: 's',
                    text: 'vary',
                    width: 'max',
                    type: 'radio',
                    theme: 'normal',
                    disabled: !hasWriteAccess ? 'yes' : '',
                },
                text: ctx.i18n(`id-type-${type}`),
                val: type,
                items: bemBlock._DEVICES_ID_TYPES.map((itemType) => ({
                    val: itemType,
                    text: ctx.i18n(`id-type-${itemType}`),
                })),
            };

            BN(block)._setContent(ctx, !hasWriteAccess, content, ctx.i18n(`id-type-${type}`));
        },

        /**
         * @prop {string} purpose
         * @prop {boolean} hasWriteAccess
         */
        'purpose' (ctx) {
            const blockDecl = BN(ctx.getName());
            const {
                purpose = blockDecl._DEFAULT_PURPOSE,
                hasWriteAccess,
            } = ctx.params();
            const purposeText = ctx.i18n(`purpose-${purpose}`);

            const content = {
                block: 'select2',
                control: true,
                name: 'purpose',
                mods: {
                    size: 's',
                    text: 'vary',
                    width: 'max',
                    type: 'radio',
                    theme: 'normal',
                    disabled: !hasWriteAccess ? 'yes' : '',
                },
                text: purposeText,
                val: purpose,
                items: blockDecl._PURPOSE_TYPES.map((purposeType) => ({
                    val: purposeType,
                    text: ctx.i18n(`purpose-${purposeType}`),
                })),
            };

            blockDecl._setContent(ctx, !hasWriteAccess, content, purposeText);
        },
    },
});

(BEM.DOM || BEM).decl('application-settings-lists', null, {
    /**
     * List of device ID types
     */
    _DEVICES_ID_TYPES: [
        'appmetrica_device_id',
        'ios_ifa',
        'ios_ifv',
        'google_aid',
        'windows_aid',
        'huawei_oaid',
    ],
    _DEFAULT_ID_TYPE: 'ios_ifa',

    /**
     * Test device purposes
     */
    _PURPOSE_TYPES: [
        'reattribution',
        'push_notifications',
    ],

    _DEFAULT_PURPOSE: 'reattribution',

    _TEST_DEVICES_CELL_DECLS: [
        {
            name: 'header-name',
            elem: 'name',
            pickDataParams: 'name',
        },
        {
            name: 'header-id',
            elem: 'device-id',
            pickDataParams: 'device_id',
            width: 330,
        },
        {
            name: 'header-id-type',
            elem: 'type',
            pickDataParams: 'type',
            width: 130,
        },
        {
            name: 'header-purpose',
            elem: 'purpose',
            pickDataParams: 'purpose',
            width: 165,
        },
        {
            elem: 'control',
            pickDataParams: 'id',
            width: 100,
        },
    ],

});
