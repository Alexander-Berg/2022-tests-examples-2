import {Undefinable, findByData, findElement} from '@txi-autotests/ts-utils';

import {BasePage} from '../base.page';

class CreatePage extends BasePage {
    @findByData('settings_data-sources_source_form_name')
    private nameInput: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_form_type')
    private typeSelector: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_form_cluster')
    private clusterSelector: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_form_path')
    private pathInput: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_form_is-partitioned')
    private partitionedBtn: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_form_partition-key')
    private keyInput: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_form_partition-template')
    private templateInput: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_form_description')
    private descriptionInput: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_form_submit-button')
    private submitBtn: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_form_cancel-button')
    private cancelBtn: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_form_reset-button')
    private resetBtn: Undefinable<ReturnType<typeof $>>;

    @findElement('.ant-drawer-close')
    private closeBtn: Undefinable<ReturnType<typeof $>>;
}

export const createPage = new CreatePage();
