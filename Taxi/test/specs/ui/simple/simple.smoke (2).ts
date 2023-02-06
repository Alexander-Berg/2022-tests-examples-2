import allureReporter from '@wdio/allure-reporter';

import dataSources from '../../../fixtures/dataSources.json';
import dataSourcesForUpdate from '../../../fixtures/dataSourcesForUpdate.json';
import {atlasPages} from '../../../page-objects';
import {authViaAqua} from  '../../../utils/auth';
import {sleep} from '../../../utils/sleep';

describe('edit data source.smoke', function () {
    before(async () => {
        await authViaAqua();

        // TODO как передавать стенд?
        await atlasPages.atlasBasePage.open('/settings/data-sources');
        await sleep(3000);

        await atlasPages.dataSources.findAndDeleteDataSource(dataSourcesForUpdate.original);
        await atlasPages.dataSources.findAndDeleteDataSource(dataSourcesForUpdate.updated);

        expect((await atlasPages.dataSources.findDataSourceName(dataSourcesForUpdate.original.name)).isFound).toBe(false);
        expect((await atlasPages.dataSources.findDataSourceByClusterAndPath(dataSourcesForUpdate.original.cluster, dataSourcesForUpdate.original.path)).isFound).toBe(false);

        expect((await atlasPages.dataSources.findDataSourceName(dataSourcesForUpdate.updated.name)).isFound).toBe(false);
        expect((await atlasPages.dataSources.findDataSourceByClusterAndPath(dataSourcesForUpdate.updated.cluster, dataSourcesForUpdate.updated.path)).isFound).toBe(false);

    });

    it('should be able to edit data source ', async () => {
        allureReporter.addTestId('atlas_settings-13');

        // сначала создаем источник данных, но не проверяем отображение в таблице/карточке просмотра (проверяем только факт, что создали что-то)
        // TODO как передавать стенд?
        await atlasPages.atlasBasePage.open('/settings/data-sources');
        await sleep(3000);

        await atlasPages.dataSources.clickAddBtn();

        expect(await atlasPages.create.pageTitle).toHaveText('Создание');

        await atlasPages.create.createDataSource(dataSourcesForUpdate.original);
        await sleep(7000);

        // проверяем, что в списке есть созданный источник
        const elemFinder = await atlasPages.dataSources.findDataSourceName(dataSourcesForUpdate.original.name);

        expect(elemFinder.isFound).toBe(true);
        // тут закончили создание источника

        const dataSourceId =  await atlasPages.dataSources.getElemId(dataSourcesForUpdate.original.name);

        expect(dataSourceId.isFound).toBe(true);
        if (dataSourceId.isFound) {
            await atlasPages.atlasBasePage.open('/settings/data-sources/edit/' + dataSourceId.foundId + '/data-source');
            await sleep(3000);

            expect(await atlasPages.create.pageTitle).toHaveText('Редактирование');
            // проверить заполненность все полей формы, что соответствуют dataSources
            const myDataSource = await atlasPages.create.getDataSourceFromUpdatePage();

            // "Имя источника отображается в карточке редактирования источника неверно")
            expect(myDataSource.name).toEqual(dataSourcesForUpdate.original.name);
            // "Тип источника отображается в карточке редактирования источника неверно");
            expect(myDataSource.type.toLowerCase()).toEqual(dataSourcesForUpdate.original.type.toLowerCase());
            // "Кластер источника отображается в карточке редактирования источника неверно");
            expect(myDataSource.cluster.toLowerCase()).toEqual(dataSourcesForUpdate.original.cluster.toLowerCase());
            // "Путь до источника отображается в карточке редактирования источника неверно")
            expect(myDataSource.path).toEqual(dataSourcesForUpdate.original.path);
            // "Секционированность источника отображается в карточке редактирования источника неверно")
            expect(myDataSource.isPartitioned).toEqual(dataSourcesForUpdate.original.isPartitioned);

            if (dataSourcesForUpdate.original.isPartitioned) {
                expect(myDataSource.key).toEqual(dataSourcesForUpdate.original.key);
                expect(myDataSource.template).toEqual(dataSourcesForUpdate.original.template);
            }

            // теперь редактируем источник данных
            await atlasPages.create.updateDataSource(dataSourcesForUpdate.updated);
            await sleep(7000);

            // TODO находимся в окне просмотра источника, можно там проверить все поля

            // тут проверяю наличие по имени в таблице
            // TODO хотелось бы проверять все поля в таблице, надо подумать над тест-дизайном
            await atlasPages.atlasBasePage.open('/settings/data-sources');
            await sleep(3000);
            const elemFinder = await atlasPages.dataSources.findDataSourceName(dataSourcesForUpdate.updated.name);

            expect(elemFinder.isFound).toBe(true);
            // TODO мне очень не нравится сколько места в кейсе это занимает, плюс это дублирует код со строки 168
            // думаю, что можно все-таки не проверять каждую строку отдельным expect (и вынести все в функцию, оставив тут один общий expect)
            // но меня эта идея смущает тем, что не будет прозрачно в каком поле ошибка (хотя надо уточнить продуктово, нужно ли такое проверять вообще?)
            // других идей пока нет. нужны идеи
            if (elemFinder.isFound) {
                // возвращаем значения из таблицы для этого источника
                const myDataSource = await atlasPages.dataSources.getDataSourceFromTable(elemFinder.foundId);
                // проверяем, что заполнено правильно
                // не поняла как к expect прикрутить message

                // "Имя созданного источника отображается в таблице неверно")
                expect(myDataSource.name).toEqual(dataSourcesForUpdate.updated.name);
                // "Тип созданного источника отображается в таблице неверно");
                expect(myDataSource.type).toEqual(dataSourcesForUpdate.updated.type.toLowerCase());
                // "Кластер созданного источника отображается в таблице неверно");
                expect(myDataSource.cluster).toEqual(dataSourcesForUpdate.updated.cluster.toLowerCase());
                // "Путь до созданного источника отображается в таблице неверно")
                expect(myDataSource.path).toEqual(dataSourcesForUpdate.updated.path);
                // "Секционированность источника отображается в таблице неверно")
                expect(myDataSource.isPartitioned).toEqual(dataSourcesForUpdate.updated.isPartitioned);

                if (dataSourcesForUpdate.updated.isPartitioned) {
                    expect(myDataSource.key).toEqual(dataSourcesForUpdate.updated.key);
                    expect(myDataSource.template).toEqual(dataSourcesForUpdate.updated.template);
                }
                else{
                    expect(myDataSource.key).toEqual('Не указано');
                    expect(myDataSource.template).toEqual('Не указано');
                }

                // переходим в окно Просмотр Источника Данных https://atlas-unstable.taxi.tst.yandex-team.ru/settings/data-sources/view/{id}/data-source
                // тут переходим по нажатию на строку
                await atlasPages.dataSources.clickRow(elemFinder.foundId);
                await sleep (3000);

                // возвращает все значения из окна Просмотр Источника данных
                const myDataSource2 = await atlasPages.view.getDataSourceView();

                // "Имя созданного источника отображается в карточке просмотра источника неверно")
                expect(myDataSource2.name).toEqual(dataSourcesForUpdate.updated.name);
                // "Тип созданного источника отображается в карточке просмотра источника неверно");
                expect(myDataSource2.type).toEqual(dataSourcesForUpdate.updated.type.toLowerCase());
                // "Кластер созданного источника отображается в карточке просмотра источника неверно");
                expect(myDataSource2.cluster).toEqual(dataSourcesForUpdate.updated.cluster.toLowerCase());
                // "Путь до созданного источника отображается в карточке просмотра источника неверно")
                expect(myDataSource2.path).toEqual(dataSourcesForUpdate.updated.path);
                // "Секционированность исчточника отображается в карточке просмотра источника неверно")
                expect(myDataSource.isPartitioned).toEqual(dataSourcesForUpdate.updated.isPartitioned);

                if (dataSourcesForUpdate.updated.isPartitioned) {
                    expect(myDataSource2.key).toEqual(dataSourcesForUpdate.updated.key);
                    expect(myDataSource2.template).toEqual(dataSourcesForUpdate.updated.template);
                }

            }
        }
    });
});

describe('create data source.smoke', function () {
    before(async () => {
        await authViaAqua();
    });
    dataSources.forEach(function (test) {
        before(async () => {
            // TODO как передавать стенд?
            await atlasPages.atlasBasePage.open('/settings/data-sources');
            await sleep(3000);
            await atlasPages.dataSources.findAndDeleteDataSource(test.source);

            expect((await atlasPages.dataSources.findDataSourceName(test.source.name)).isFound).toBe(false);
            expect((await atlasPages.dataSources.findDataSourceByClusterAndPath(test.source.cluster, test.source.path)).isFound).toBe(false);
        });
    });
    dataSources.forEach(function (test) {
        it('should be able to add data source ' + test.source.id, async () => {allureReporter.addTestId('atlas_settings-' + test.source.atlas_id);

            // TODO как передавать стенд?
            await atlasPages.atlasBasePage.open('/settings/data-sources');
            await sleep(3000);

            await atlasPages.dataSources.clickAddBtn();
            await atlasPages.create.createDataSource(test.source);

            await sleep(7000);
            // TODO проверять, что вышла подсказка, что источник "Создано"
            // нотификации стакаются, надо это обработать
            // await atlasPages.dataSources.waitForNotification();

            // проверяем, что в списке есть созданный источник
            const elemFinder = await atlasPages.dataSources.findDataSourceName(test.source.name);

            expect(elemFinder.isFound).toBe(true);

            if (elemFinder.isFound) {
                // возвращаем значения из таблицы для этого источника
                const myDataSource = await atlasPages.dataSources.getDataSourceFromTable(elemFinder.foundId);
                // проверяем, что заполнено правильно
                // не поняла как к expect прикрутить message

                expect(myDataSource.name).toEqual(test.source.name); // "Имя созданного источника отображается в таблице неверно")
                expect(myDataSource.type).toEqual(test.source.type.toLowerCase());// "Тип созданного источника отображается в таблице неверно");
                expect(myDataSource.cluster).toEqual(test.source.cluster.toLowerCase());// "Кластер созданного источника отображается в таблице неверно");
                expect(myDataSource.path).toEqual(test.source.path);// "Путь до созданного источника отображается в таблице неверно")
                expect(myDataSource.isPartitioned).toEqual(test.source.isPartitioned);// "Секционированность исчточника отображается в таблице неверно")

                if (test.source.isPartitioned) {
                    expect(myDataSource.key).toEqual(test.source.key);
                    expect(myDataSource.template).toEqual(test.source.template);
                }
                else{
                    expect(myDataSource.key).toEqual('Не указано');
                    expect(myDataSource.template).toEqual('Не указано');
                }

                // переходим в окно Просмотр Источника Данных https://atlas-unstable.taxi.tst.yandex-team.ru/settings/data-sources/view/{id}/data-source
                // тут переходим по нажатию на строку
                await atlasPages.dataSources.clickRow(elemFinder.foundId);
                await sleep (3000);

                // возвращает все значения из окна Просмотр Источника данных
                const myDataSource2 = await atlasPages.view.getDataSourceView();

                expect(myDataSource2.name).toEqual(test.source.name); // "Имя созданного источника отображается в карточке просмотра источника неверно")
                expect(myDataSource2.type).toEqual(test.source.type.toLowerCase());// "Тип созданного источника отображается в карточке просмотра источника неверно");
                expect(myDataSource2.cluster).toEqual(test.source.cluster.toLowerCase());// "Кластер созданного источника отображается в карточке просмотра источника неверно");
                expect(myDataSource2.path).toEqual(test.source.path);// "Путь до созданного источника отображается в карточке просмотра источника неверно")
                expect(myDataSource.isPartitioned).toEqual(test.source.isPartitioned);// "Секционированность исчточника отображается в карточке просмотра источника неверно")

                if (test.source.isPartitioned) {
                    expect(myDataSource2.key).toEqual(test.source.key);
                    expect(myDataSource2.template).toEqual(test.source.template);
                }

            }
        });
    });
});


