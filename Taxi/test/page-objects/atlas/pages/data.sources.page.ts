import {findByData, findElement, findMultipleByData, Undefinable} from '@txi-autotests/ts-utils';

import {atlasPages} from '../../index';
import {atlasBasePage, AtlasBasePage, DataSource} from '../atlas.base.page';


type FoundRow =
    | { isFound: false }
    | {
        isFound: true;
        foundId: number;
    }


class DataSourcesPage extends AtlasBasePage {

    // кнопки над шапкой таблицы
    @findByData('settings_data-sources_table_add-button')
    private addBtn: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_table_column-picker-button')
    private columnPickerBtn: Undefinable<ReturnType<typeof $>>;

    // поля таблицы
    @findMultipleByData('settings_data-sources_table_name-value')
    private nameValues: Undefinable<ReturnType<typeof $>>;

    @findMultipleByData('settings_data-sources_table_type-value')
    private typeValues: Undefinable<ReturnType<typeof $>>;

    @findMultipleByData('settings_data-sources_table_cluster-value')
    private clusterValues: Undefinable<ReturnType<typeof $>>;

    @findMultipleByData('settings_data-sources_table_path-value')
    private pathValues: Undefinable<ReturnType<typeof $>>;

    @findMultipleByData('settings_data-sources_table_is-partitioned-value')
    private isPartitionedValues: Undefinable<ReturnType<typeof $>>;

    @findMultipleByData('settings_data-sources_table_partition-key-value')
    private keyValues: Undefinable<ReturnType<typeof $>>;

    @findMultipleByData('settings_data-sources_table_partition-template-value')
    private templateValues: Undefinable<ReturnType<typeof $>>;

    // другие поля, которые можно добавить в таблицу через кнопку Колонки columnPickerBtn (пока не используются)
    // settings_data-sources_table_id-value
    // settings_data-sources_table_author-value
    // settings_data-sources_table_created-at-value
    // settings_data-sources_table_data-updated-at-value
    // settings_data-sources_table_changed-by-value
    // settings_data-sources_table_changed-at-value

    @findMultipleByData('settings_data-sources_table_delete-button')
    private  deleteButtons: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_table_delete-popconfirm-cancel')
    private deleteButtonCancel: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_table_delete-popconfirm-confirm')
    private deleteButtonConfirm: Undefinable<ReturnType<typeof $>>;

    @findByData('settings_data-sources_table_edit-button')
    private editButtons: Undefinable<ReturnType<typeof $>>;

    @findElement('.ant-notification-close-x')
    private closeNotificationBtn: Undefinable<ReturnType<typeof $>>;



    public async clickAddBtn() {
        const addBtn = await this.addBtn;

        await addBtn?.click();
    }

    public async clickColumnPickerBtn() {
        const columnPickerBtn = await this.columnPickerBtn;

        await columnPickerBtn?.click();
    }

    public async clickRow(rowId: number) {
        const nameValues = (await this.nameValues) as any as WebdriverIO.Element[];
        const nameValue = nameValues?.[rowId];

        await nameValue?.click();
    }

    public async waitForNotification() {
        // лучше передавать не кнопку, а весь попап
        const closeNotificationBtn = await this.closeNotificationBtn;

        await atlasBasePage.waitForElement(closeNotificationBtn);
    }

    // возвращает номер строки в таблице с искомым источником данных
    // или false
    public async findDataSourceName(name: string): Promise<FoundRow> {
        const nameValues = (await this.nameValues) as any as WebdriverIO.Element[];

        for (let i = 0; i < nameValues?.length; i++) {
            const text = await nameValues?.[i].getText();

            if (name === text) {
                return {
                    isFound: true,
                    foundId: i,
                };
            }
        }
        return {
            isFound: false,
        };
    }

    public async findDataSourceByClusterAndPath(cluster: string, path: string): Promise<FoundRow> {
        const clusterValues = (await this.clusterValues) as any as WebdriverIO.Element[];
        const pathValues = (await this.pathValues) as any as WebdriverIO.Element[];


        for (let i = 0; i < clusterValues?.length; i++) {
            const textCluster = await clusterValues?.[i].getText();
            const textPath = await pathValues?.[i].getText();


            if ((textCluster === cluster.toLowerCase()) && (textPath === path.toLowerCase())) {
                return {
                    isFound: true,
                    foundId: i,
                };
            }
        }
        return {
            isFound: false,
        };
    }

    public async getDataSourceFromTable(id: number): Promise<DataSource> {
        const nameValues = (await this.nameValues) as any as WebdriverIO.Element[];
        const typeValues = (await this.typeValues) as any as WebdriverIO.Element[];
        const clusterValues = (await this.clusterValues) as any as WebdriverIO.Element[];
        const pathValues = (await this.pathValues) as any as WebdriverIO.Element[];
        const partitionedIcon = await (await this.isPartitionedValues)?.[id].$('..').$('svg').getAttribute('data-icon');
        const keyValues = (await this.keyValues) as any as WebdriverIO.Element[];
        const templateValues = (await this.templateValues) as any as WebdriverIO.Element[];

        const name = await nameValues?.[id].getText();
        const type = await typeValues?.[id].getText();
        const cluster = await clusterValues?.[id].getText();
        const path = await pathValues?.[id].getText();
        const key = await keyValues?.[id].getText();
        const template = await templateValues?.[id].getText();

        let isPartitioned = false;

        if (partitionedIcon === 'check')
        {
            isPartitioned = true;
        }// если partitionedIcon == "close", то isPartitioned = false;


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

    public async deleteDataSource(id: number) {
        const deleteButtons = await this.deleteButtons;
        const deleteButtonConfirm = await this.deleteButtonConfirm;
        const deleteButton = deleteButtons?.[id];

        await deleteButton?.click();
        await deleteButtonConfirm?.click();
    }

    public async findAndDeleteDataSource(dataSourse: DataSource) {
        let elemFound;
        const elemFoundByName = await atlasPages.dataSources.findDataSourceName(dataSourse.name);
        const elemFoundByPath = await atlasPages.dataSources.findDataSourceByClusterAndPath(dataSourse.cluster, dataSourse.path);

        if (elemFoundByName.isFound || elemFoundByPath.isFound) {
            if (elemFoundByName.isFound) {
                elemFound = elemFoundByName;
            } else {
                elemFound = elemFoundByPath;
            }
            await atlasPages.dataSources.deleteDataSource(elemFound.foundId);
            await atlasPages.dataSources.waitForNotification();
            // TODO проверять, что вышла подсказка с текстом  "Источник успешно удален" (пока просто наличие объекта смотрю)
        }
    }

    public async getDataRowKey(rowId:number) : Promise<number>
    {
        const nameValues = (await this.nameValues) as any as WebdriverIO.Element[];
        const nameValue = await nameValues?.[rowId];

        return Number(await nameValue?.parentElement().parentElement().getAttribute('data-row-key'));
    }

    public async getElemId(name:string) : Promise<FoundRow>
    {
        const elem = await atlasPages.dataSources.findDataSourceName(name);

        if (elem.isFound){
            const id = await this.getDataRowKey(elem.foundId);

            return {
                isFound: true,
                foundId: id,
            };
        }
        return {
            isFound: false,
        };
    }
}

export const dataSourcesPage = new DataSourcesPage();
