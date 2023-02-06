import {findByData, findElement, Undefinable} from '@txi-autotests/ts-utils';

import {setValue} from '../../../utils/setValue';
import {AtlasBasePage, DataSource} from '../atlas.base.page';


class CreatePage extends AtlasBasePage {

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

    @findElement('.ant-drawer-title')
    public pageTitle: Undefinable<ReturnType<typeof $>>;


    private async clickPartitionedBtn() {
        const partitionedBtn = await this.partitionedBtn;

        await partitionedBtn?.click();
    }

    private async clickSubmitBtn() {
        const submitBtn = await this.submitBtn;

        await submitBtn?.click();
    }

    private async clickCancelBtn() {
        const cancelBtn = await this.cancelBtn;

        await cancelBtn?.click();
    }

    private async clickResetBtn() {
        const resetBtn = await this.resetBtn;

        await resetBtn?.click();
    }

    private async clickCloseBtn() {
        const closeBtn = await this.closeBtn;

        await closeBtn?.click();
    }

    private async choosePartitionedState(state: boolean) {
        const partitionedBtn = await this.partitionedBtn;
        const isPartitionedString = await partitionedBtn?.getAttribute('aria-checked');
        const isPartitioned =  isPartitionedString === 'true';

        if (state !== isPartitioned) {
            await this.clickPartitionedBtn();
        }
    }

    private async setName(name: string) {
        const nameInput = await this.nameInput;

        await setValue(nameInput,name);
    }

    private async selectFromDropDown(elementSelector: WebdriverIO.Element | undefined, toSelect: string) {
        await elementSelector?.click();
        const selectorItem = elementSelector?.$('..').$('.ant-select-dropdown').$('div='+toSelect);

        await selectorItem?.click();
    }

    private async selectType(type: string) {
        const typeSelector = await this.typeSelector;

        await this.selectFromDropDown(typeSelector, type);
    }

    private async selectCluster(cluster: string) {
        const clusterSelector = await this.clusterSelector;

        await this.selectFromDropDown(clusterSelector, cluster);
    }

    private async setPath(path: string) {
        const pathInput = await this.pathInput;

        await setValue(pathInput,path);
    }

    private async setDescription(description: string) {
        const descriptionInput = await this.descriptionInput;

        await setValue(descriptionInput,description);
    }

    private async setKey(key: string) {
        const keyInput = await this.keyInput;

        await setValue(keyInput,key);
    }

    private async setTemplate(template: string) {
        const templateInput = await this.templateInput;

        await setValue(templateInput,template);
    }

    public async createDataSource(
        dataSource: DataSource,
    ) {
        const {name, type, cluster, path, isPartitioned, key, template, description} = dataSource;

        await this.setName(name);
        await this.selectType(type);
        await this.selectCluster(cluster);
        await this.setPath(path);
        await this.choosePartitionedState(isPartitioned);

        if (isPartitioned) {
            await this.setKey(key);
            await this.setTemplate(template);
        }

        await this.setDescription(description);
        await this.clickSubmitBtn();
    }

    public async getTitleText(){
        const pageTitle = await this.pageTitle;

        return pageTitle?.getText();
    }

    // полностью передаем новый датасорс
    // TODO схлопнуть с create
    public async updateDataSource(
        newDataSource: DataSource,
    ) {
        const {name, type, cluster, path, isPartitioned, key, template, description} = newDataSource;

        await this.setName(name);
        await this.selectType(type);
        await this.selectCluster(cluster);
        await this.setPath(path);
        await this.choosePartitionedState(isPartitioned);

        if (isPartitioned) {
            await this.setKey(key);
            await this.setTemplate(template);
        }

        await this.setDescription(description);
        await this.clickSubmitBtn();
    }

    public async  getDataSourceFromUpdatePage(): Promise<DataSource>
    {
        const nameInput = await this.nameInput;
        const typeSelector = await this.typeSelector;
        const clusterSelector = await this.clusterSelector;
        const pathInput = await this.pathInput;
        const partitionedBtn = await this.partitionedBtn;
        const keyInput = await this.keyInput;
        const templateInput = await this.templateInput;
        const descriptionInput = await this.descriptionInput;

        const name = await nameInput?.getValue() as string;
        const path = await pathInput?.getValue() as string;
        const description = await descriptionInput?.getValue() as string;

        const type = await typeSelector?.getText() as string;
        const cluster = await clusterSelector?.getText() as string;

        const isPartitionedString = await partitionedBtn?.getAttribute('aria-checked');
        const isPartitioned =  isPartitionedString === 'true';

        let key = '';
        let template = '';

        if (isPartitioned){        // только если секционирована
            key = await keyInput?.getValue() as string;
            template = await templateInput?.getValue() as string;
        }

        return {
            name,
            type,
            cluster,
            path,
            isPartitioned,
            key,
            template,
            description,
        };
    }
}



export const createPage = new CreatePage();
