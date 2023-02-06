import {Undefinable, findByData, findElement} from '@txi-autotests/ts-utils';

import {AtlasBasePage, DataSource} from '../atlas.base.page';


class ViewPage extends AtlasBasePage {

    @findByData('settings_data-sources_source_card_name_value')
    private nameValue: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_card_type_value')
    private typeValue: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_card_cluster_value')
    private clusterValue: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_card_source-path_value')
    private pathValue: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_card_is-partitioned_value')
    private isPartitionedValue: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_card_partition-key_value')
    private keyValue: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_card_partition-template_value')
    private templateValue: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_card_description_value')
    private descriptionValue: Undefinable<ReturnType<typeof $>>;

    // лэйбл-заголовок название источника данных
    // добавить data-cy
    @findElement('.ant-typography')
    private headerLabel: Undefinable<ReturnType<typeof $>>;


    @findByData('settings_data-sources_source_details_edit-button')
    private editBtn: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_details_columns-extract-button')
    private extractBtn: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_source_details_delete-button')
    private deleteBtn: Undefinable<ReturnType<typeof $>>;


    public async clickEditBtn() {
        const editBtn = await this.editBtn;

        await editBtn?.click();
    }

    // по логике похоже на getDataSourceFromTable, мб можно схлопнуть
    public async  getDataSourceView(): Promise<DataSource> {
        const nameValue = await this.nameValue;
        const typeValue = await this.typeValue;
        const clusterValue = await this.clusterValue;
        const pathValue = await this.pathValue;
        const partitionedIcon = await (await this.isPartitionedValue)?.$('..').$('svg').getAttribute('data-icon');
        const keyValue = await this.keyValue;
        const templateValue = await this.templateValue;

        const name = await nameValue?.getText() as string;
        const type = await typeValue?.getText() as string;
        const cluster = await clusterValue?.getText() as string;
        const path = await pathValue?.getText() as string;

        let key = '';
        let template = '';
        let isPartitioned = false;

        if (partitionedIcon === 'check')
        {
            isPartitioned = true;
            key = await keyValue?.getText() as string;
            template = await templateValue?.getText() as string;
        }// если partitionedIcon == "close", то останутся пустые значения и isPartitioned = false;

        return {
            name,
            type,
            cluster,
            path,
            isPartitioned,
            key,
            template,
            description: '',
        };
    }
}

export const viewPage = new ViewPage();
