import {parseSpreadSheetJSON} from 'tests/e2e/helper/parse-spreadsheet';
import createArchive from 'tests/e2e/utils/create-archive';
import createImageFile from 'tests/e2e/utils/create-image-file';
import getFixturePath from 'tests/e2e/utils/fixture';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

async function expandWindowAndAssertImage(browser: WebdriverIO.Browser, selector: Hermione.Selector) {
    const initialSize = await browser.getWindowSize();

    await browser.performScroll(['import-table', '\\div', '\\div:last-child'], {
        direction: 'right',
        afterIterationDelay: () => browser.waitUntilRendered()
    });

    const [scrollWidth, containerWidth] = await browser.execute(() => [
        document.querySelector('[data-testid=import-table] div div:last-child div')?.getBoundingClientRect().width,
        document.querySelector('[data-testid=import-table] div div:last-child')?.getBoundingClientRect().width
    ]);

    if (!scrollWidth) {
        throw new Error('scroll width of "import-table" is undefined');
    }

    if (!containerWidth) {
        throw new Error('container width of "import-table" is undefined');
    }

    const expandedWidth = initialSize.width + (scrollWidth - containerWidth);

    await browser.setWindowSize(expandedWidth, initialSize.height);
    await browser.assertImage(selector);
    await browser.setWindowSize(initialSize.width, initialSize.height);
}

describe('Импорт', function () {
    it('Страница импорта – общий вид', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.waitUntilRendered();
        await this.browser.assertImage({screenshotDelay: 1000});
    });

    it('Шаблон файла для импорта', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        const link = await this.browser.findByTestId('xlsx-template-link');
        const url = await link.getProperty('href');
        expect(url).to.match(new RegExp('templates/import-spreadsheet_ru_rev\\d.xlsx'));
    });

    it('Шаблон архива для импорта с изображением', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        const link = await this.browser.findByTestId('zip-template-link');
        const url = await link.getProperty('href');
        expect(url).to.match(new RegExp('templates/import-archive_rev\\d.zip'));
    });

    it('Шаблон архива для импорта мета-товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        const link = await this.browser.findByTestId('meta-product-template-link');
        const url = await link.getProperty('href');
        expect(url).to.match(new RegExp('templates/import-meta-products-archive_ru_rev\\d.zip'));
    });

    it('Ошибка при импорте товара из другого региона', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-with-different-product-regions.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-not-upload');
    });

    it('Пустая ячейка для изображения не удаляет картинку', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-with-empty-image.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT('10000001'));
        await this.browser.waitForTestIdSelectorInDom(['product-image', 'thumbnail', 'image']);
        await this.browser.assertImage('product-image');
    });

    it('Ошибка при импорте архива с картинкой больше 5МБ', async function () {
        const imageName = 'import_big_image.png';
        const imagePath = createImageFile(imageName, 2400);
        const archiveName = 'import_big_image_archive.zip';
        const archivePath = await createArchive(archiveName, [imagePath]);

        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        const inputSelector = ['import-upload', 'file-input'];
        await this.browser.uploadFileInto(inputSelector, archivePath);

        const filenameEl = await this.browser.findByTestId(['import-upload', 'upload-file_filename']);

        expect(await filenameEl.getText()).to.equal(archiveName);
        await this.browser.assertImage('import-upload');
    });

    it('Создать товар и изменить товар одним файлом', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-create-and-update-products.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-create');
        await this.browser.waitForTestIdSelectorInDom('import-info-update');

        await this.browser.clickInto(['import-info-create', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});

        await expandWindowAndAssertImage(this.browser, 'import-info-create');
        await expandWindowAndAssertImage(this.browser, 'import-info-update');
    });

    it('Импорт пустого значения в необязательном поле', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-empty-field-in-optional-attribute.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Импорт всех типов атрибутов при создании товара в RU, без кода для локализуемых атрибутов', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-all-type-of-attributes-in-russia.zip')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-create');
        await this.browser.clickInto(['import-info-create', 'expand-icon'], {waitRender: true});
        await expandWindowAndAssertImage(this.browser, 'import-info-create');
    });

    it('Импорт всех типов атрибутов при изменении товара во FR', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS, {region: 'fr'});
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-all-type-of-attributes-in-france.zip')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await expandWindowAndAssertImage(this.browser, 'import-info-update');
    });

    it('Замена JPG в корне архива', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('upload-images-via-archive-root.zip')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Замена PNG в папке архива', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('upload-images-via-archive-folder.zip')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Не заменять изображение, если указана ссылка на то же изображение', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('not-upload-images-with-same-url.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-ignore');
        await this.browser.clickInto(['import-info-ignore', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-ignore');
    });

    it('Импорт с модификацией добавления &', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-with-add-modifier.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Импорт с модификацией удаления _', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-with-subtract-modifier.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Импорт пустого множественного изображения', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-empty-multiple-image.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-ignore');
        await this.browser.assertImage('header');
        await this.browser.assertImage('import-info-ignore');
    });

    it('Импорт множественных изображений для товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(['import-upload', 'file-input'], getFixturePath('import-multiple-image.zip'));
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT('10000001'));
        await this.browser.waitForTestIdSelectorInDom(['product-image', 'thumbnail', 'image']);
        await this.browser.assertImage('product-image');
    });

    it('Импорт изображений по баркодам на два товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-images-by-barcode.zip')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT('10000001'));
        await this.browser.waitForTestIdSelectorInDom(['product-image', 'thumbnail', 'image']);
        await this.browser.assertImage('product-image');
    });

    it('Импорт изображения по несуществующему баркоду', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        const archiveName = 'import-image-by-wrong-barcode.zip';
        await this.browser.uploadFileInto(['import-upload', 'file-input'], getFixturePath(archiveName));

        const filenameEl = await this.browser.findByTestId(['import-upload', 'upload-file_filename']);

        expect(await filenameEl.getText()).to.equal(archiveName);
        await this.browser.assertImage('import-upload');
    });

    it('Импорт большого изображения по баркоду', async function () {
        const imageName = '3286357016302.png';
        const imagePath = createImageFile(imageName, 2400);
        const archiveName = 'import_big_image_by_barcode_archive.zip';
        const archivePath = await createArchive(archiveName, [imagePath]);

        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(['import-upload', 'file-input'], archivePath);

        const filenameEl = await this.browser.findByTestId(['import-upload', 'upload-file_filename']);

        expect(await filenameEl.getText()).to.equal(archiveName);
        await this.browser.assertImage('import-upload');
    });

    it('Импорт изображения по баркоду из другого региона', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        const archiveName = 'import-image-by-barcode-from-another-region.zip';
        await this.browser.uploadFileInto(['import-upload', 'file-input'], getFixturePath(archiveName));

        const filenameEl = await this.browser.findByTestId(['import-upload', 'upload-file_filename']);
        expect(await filenameEl.getText()).to.equal(archiveName);
        await this.browser.assertImage('import-upload');
    });

    it('Попытка импорта изображения по баркоду, когда изображение неиспользуемый атрибут', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-image-by-barcode-to-product-without-image.zip')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-ignore');
        await this.browser.clickInto(['import-info-ignore', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('header');
        await this.browser.assertImage('import-info-ignore');
    });

    it('При импорте изображения по баркодам товар не ищется в другом регионе', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-image-by-barcode-foreign-region-gb.zip')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Изменить на false пустой атрибут через импорт', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-boolean-attribute-from-unset-to-false.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Изменить на true пустой атрибут через импорт', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-boolean-attribute-from-unset-to-true.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Очистить false-атрибут через импорт', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-boolean-attribute-from-false-to-unset.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Очистить true-атрибут через импорт', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-boolean-attribute-from-true-to-unset.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Отсутствуют изменения при импорте пустой ячейки для атрибута, который не определен', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-boolean-attribute-from-unset-to-unset.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-ignore');
        await this.browser.clickInto(['import-info-ignore', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-ignore');
    });

    it('Превью изображений в импорте – раскрыть изображение по клику из импорта', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(['import-upload', 'file-input'], getFixturePath('import-multiple-image.zip'));
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('thumbnail', {waitRender: true});
        await this.browser.assertImage('image-view-modal', {removeShadows: true});
    });

    it('Экспорт после импорта', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(['import-upload', 'file-input'], getFixturePath('import-multiple-image.zip'));
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.clickInto('download-xlsx-link', {waitRender: true});
        const file = await this.browser.getDownloadedFile('exported-products.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Смена мастер-категории с появлением неиспользуемых и удалением пустых атрибутов', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000021));

        const elements = await Promise.all(
            [
                'string_attribute_code_5_1__0_remove',
                'string_attribute_code_5_1__1_remove',
                'string_attribute_code_5_1__2_remove'
            ].map((selector) => this.browser.findByTestId(selector))
        );

        for (const element of elements) {
            await element.click();
        }

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-master-category-for-unused-attributes.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT(10000021));
        await this.browser.waitForTestIdSelectorNotInDom('^string_attribute_code_5_1');
        await this.browser.assertImage('unused-attributes', {removeShadows: true});
    });

    it('Ошибка при создании товара с пустой мастер-категорией', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('create-product-with-empty-master-category.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-not-upload');
    });

    it('Пустая мастер-категория и изменение другого атрибута товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('update-product-with-empty-master-category.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-not-upload');
    });

    it('Неизменный атрибут можно задать через импорт', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('create-immutable-attribute-value.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Неизменный атрибут нельзя изменить через импорт', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('change-immutable-attribute-value.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-ignore');
        await this.browser.clickInto(['import-info-ignore', 'expand-icon'], {waitRender: true});
        const tooltipIcon = await this.browser.findByTestId('import-cell-tooltip-help-icon');
        await tooltipIcon.moveTo();

        await this.browser.assertImage('import-info-ignore');
    });

    it('Ошибка при загрузке пустого архива', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(['import-upload', 'file-input'], getFixturePath('empty-archive.zip'));
        await this.browser.waitForTestIdSelectorInDom('upload-file_description');
        await this.browser.assertImage('import-upload');
    });

    it('Ошибка при загрузке архива с файлом неправильного формата', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('archive-with-wrong-file.zip')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-ignore');
        await this.browser.clickInto(['import-info-ignore', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-ignore');
    });

    it('Ошибка при загрузке архива без таблицы и без штрихкода в названии изображения', async function () {
        const imagePath = createImageFile('image.png');
        const archivePath = await createArchive('archive_without_table.zip', [imagePath]);

        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(['import-upload', 'file-input'], archivePath);
        await this.browser.waitForTestIdSelectorInDom('upload-file_description');
        await this.browser.assertImage('import-upload');
    });

    it('Ошибка при создании товара в родительской категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('create-product-with-parent-master-category.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-not-upload');
    });

    it('Импортировать изображение по баркодам где фото со сторонами меньше 800', async function () {
        const imageName = '3286357016302.png';
        const imagePath = createImageFile(imageName, 250);
        const archiveName = 'import_invalid_resolution_image_by_barcode_archive.zip';
        const archivePath = await createArchive(archiveName, [imagePath]);

        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(['import-upload', 'file-input'], archivePath);

        await this.browser.waitForTestIdSelectorInDom('import-info-ignore');
        await this.browser.clickInto(['import-info-ignore', 'expand-icon'], {waitRender: true});
        const tooltipIcon = await this.browser.findByTestId('import-cell-tooltip-help-icon');
        await tooltipIcon.moveTo();

        await this.browser.assertImage('import-info-ignore');
    });

    it('Импортировать множественное фото где одно изображение со сторонами меньше 800', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-multiple-image-with-wrong-resolution.zip')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-ignore');
        await this.browser.clickInto(['import-info-ignore', 'expand-icon'], {waitRender: true});
        const tooltipIcon = await this.browser.findByTestId('import-cell-tooltip-help-icon');
        await tooltipIcon.moveTo();

        await this.browser.assertImage('import-info-ignore');
    });

    // eslint-disable-next-line max-len
    it('Импортировать главное фото через классический архив с таблицей и фото со сторонами меньше 800', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-image-with-wrong-resolution.zip')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-ignore');
        await this.browser.clickInto(['import-info-ignore', 'expand-icon'], {waitRender: true});
        const tooltipIcon = await this.browser.findByTestId('import-cell-tooltip-help-icon');
        await tooltipIcon.moveTo();

        await this.browser.assertImage('import-info-ignore');
    });

    it('Тип номенклатуры товара во Франции нельзя очистить через импорт', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS, {region: 'fr'});

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-empty-nomenclature-type.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-ignore');
        await this.browser.clickInto(['import-info-ignore', 'expand-icon'], {waitRender: true});
        const tooltipIcon = await this.browser.findByTestId('import-cell-tooltip-help-icon');
        await tooltipIcon.moveTo();

        await this.browser.assertImage('import-info-ignore');
    });

    it('Нельзя создать товар с некорректным типом номенклатуры через импорт', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('create-product-with-wrong-nomenclature-type.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});

        await this.browser.assertImage('import-info-not-upload');
    });

    it('Ошибка при превышении лимита на создание товаров', async function () {
        // Для e2e лимит установлен равным 20-ти товарам
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);
        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('create-too-many-products.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('upload-file_description');
        await this.browser.assertImage('import-upload');
    });

    it('Можно импортировать только разрешенные форматы для атрибутов-изображений', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-image-with-wrong-extension.zip')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');

        await this.browser.waitForTestIdSelectorInDom('import-info-ignore');
        await this.browser.clickInto(['import-info-ignore', 'expand-icon'], {waitRender: true});
        const tooltipIcon = await this.browser.findByTestId('import-cell-tooltip-help-icon');
        await tooltipIcon.moveTo();
        await this.browser.assertImage('import-info-ignore');

        await this.browser.clickInto(['header-panel', 'submit-button']);

        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT('10000001'));
        await this.browser.waitForTestIdSelectorInDom(['product-image', 'thumbnail', 'image']);
        await this.browser.assertImage('product-image');
    });

    it('Можно импортировать только разрешенные форматы для атрибутов-изображений (баркод)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-images-with-wrong-extensions-barcode.zip')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');

        await this.browser.waitForTestIdSelectorInDom('import-info-ignore');
        await this.browser.clickInto(['import-info-ignore', 'expand-icon'], {waitRender: true});
        const tooltipIcon = await this.browser.findByTestId('import-cell-tooltip-help-icon');
        await tooltipIcon.moveTo();
        await this.browser.assertImage('import-info-ignore');

        await this.browser.clickInto(['header-panel', 'submit-button']);

        await this.browser.waitForTestIdSelectorInDom('import-success-alert');

        await this.browser.openPage(ROUTES.CLIENT.PRODUCT('10000001'));
        await this.browser.waitForTestIdSelectorInDom(['product-image', 'thumbnail', 'image']);
        await this.browser.assertImage('product-image');
    });

    it('В импорте читается первый не скрытый лист', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-with-hidden-sheet.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    it('Если первый не скрытый лист невалидный, то показываем сообщение с ошибкой', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-with-first-invalid-sheet.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('upload-file_description');
        await this.browser.assertImage('import-upload');
    });

    it('Показ модального окна при подготовке Импорта', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.setNetworkConditions({latency: 2500, download_throughput: 25600, upload_throughput: 51200});

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-all-type-of-attributes-in-russia.zip')
        );

        await this.browser.waitForTestIdSelectorVisible('message-modal');
        await this.browser.assertImage('message-modal', {removeShadows: true});

        await this.browser.setNetworkConditions({}, 'No throttling');
    });

    it('Показ модального окна при применении Импорта', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-all-type-of-attributes-in-russia.zip')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-create');

        await this.browser.setNetworkConditions({latency: 2500, download_throughput: 25600, upload_throughput: 51200});

        await this.browser.clickInto(['header-panel', 'submit-button']);
        await this.browser.waitForTestIdSelectorVisible('message-modal');
        await this.browser.assertImage('message-modal', {removeShadows: true});

        await this.browser.setNetworkConditions({}, 'No throttling');
    });

    // eslint-disable-next-line max-len
    it('Нельзя создать товары с одинаковым штрихкодом, отличающимся наличием скрытого символа, через импорт', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('create-product-with-hidden-char-in-barcode.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-not-upload');
    });

    it('Импорт изображений по баркодам вложенных в папку на два товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-images-by-barcode-in-folder.zip')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');

        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('import-success-alert');
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT('10000001'));
        await this.browser.waitForTestIdSelectorInDom(['product-image', 'thumbnail', 'image']);
        await this.browser.assertImage('product-image');
    });

    // eslint-disable-next-line max-len
    it('Изображения по баркодам загружаются импортом из архива с двумя уровнями, фотографии есть в каждом уровне', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-images-by-barcode-in-root-and-folder.zip')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-update');
        await this.browser.clickInto(['import-info-update', 'expand-icon'], {waitRender: true});
        await this.browser.assertImage('import-info-update');
    });

    // eslint-disable-next-line max-len
    it('Нотификация появляется при импорте невалидного кода ФК (такой ФК нет) при обновлении товара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS);

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-wrong-front-category.xlsx')
        );

        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-not-upload');
    });

    // eslint-disable-next-line max-len
    it('Нотификация появляется при импорте невалидного кода ФК (используется родительская ФК) при создании товара, Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.IMPORT_PRODUCTS, {region: 'il'});

        await this.browser.uploadFileInto(
            ['import-upload', 'file-input'],
            getFixturePath('import-parent-front-category.xlsx')
        );
        await this.browser.waitForTestIdSelectorInDom('import-info-not-upload');
        await this.browser.clickInto(['import-info-not-upload', 'expand-icon'], {waitRender: true});
        await this.browser.clickInto('import-cell-tooltip-help-icon', {waitRender: true});
        await this.browser.assertImage('import-info-not-upload');
    });
});
