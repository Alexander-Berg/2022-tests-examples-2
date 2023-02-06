package ru.yandex.metrika.cdp.api.tests.medium.service.schemaservice;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.function.Consumer;

import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.web.multipart.MultipartFile;

import ru.yandex.metrika.cdp.dto.schema.EntityNamespace;
import ru.yandex.metrika.cdp.dto.uploading.ApiValidationStatus;
import ru.yandex.metrika.cdp.dto.uploading.UploadingFormat;
import ru.yandex.metrika.cdp.dto.uploading.UploadingMeta;
import ru.yandex.metrika.cdp.dto.uploading.UploadingStatus;
import ru.yandex.metrika.cdp.frontend.data.CSVColumnNames;
import ru.yandex.metrika.cdp.frontend.data.DelimiterType;
import ru.yandex.metrika.cdp.frontend.schema.rows.ListItemRow;
import ru.yandex.metrika.util.io.IOUtils;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractSchemaServiceTest.SchemaConfig.class})
public class UploadCustomListItemsTest extends AbstractSchemaServiceSaveListTest {

    UploadingMeta uploadingMeta;

    static final String LIST_ITEM_COLUMNS_MAPPING = "\"name\":\"Имя\",\"humanized\":\"Человекочитаемое имя\"," +
            "\"day_the_earth_stood_still\":\"Дата КЗО\",\"names_of_pet\":\"Имена животных\"";

    @Before
    public void testBody() {
        customList = getCustomList();
        schemaService.saveList(getCounterId(), customList);

        byte[] fileContent = IOUtils
                .resourceAsString(UploadCustomListItemsTest.class, "./csv/test_list_items.csv").getBytes();
        MultipartFile multipartFileWithListItems = new MockMultipartFile("List_items.csv", fileContent);
        CSVColumnNames listItemsMapping = new CSVColumnNames(LIST_ITEM_COLUMNS_MAPPING);

        uploadingMeta = schemaService.uploadCustomListItems(getCounterId(),
                customList.getName(),
                listItemsMapping,
                DelimiterType.SEMICOLON,
                multipartFileWithListItems);
        updateDataAboutCustomListAfterUploading();

        expectedItems = parseRows(listItemsMapping,
                multipartFileWithListItems,
                EntityNamespace.customListNamespace(customList.getName()),
                ListItemRow.class);
        updateItemsInfoAfterUploading();
    }

    @Parameterized.Parameters(name = "{1}")
    public static List<Object[]> getParameters() {
        var tests = new ArrayList<Object[]>();
        tests.addAll(getCommonListTests());
        tests.addAll(Arrays.asList(
                new Object[][]{
                        {c(test -> assertEquals(Integer.valueOf(test.expectedItems.size()),
                                test.uploadingMeta.getElementsCount())), "Тест количества загруженных элементов списка"},
                        {c(test -> assertTrue(
                                test.uploadingMeta.getUploadingStatus().equals(UploadingStatus.COMPLETED) ||
                                        test.uploadingMeta.getUploadingStatus().equals(UploadingStatus.IN_PROCESS))),
                                "Тест статуса загрузки"},
                        {c(test -> assertEquals(UploadingFormat.CSV, test.uploadingMeta.getUploadingFormat())),
                                "Тест формата загруженных данных"},
                        {c(test -> assertEquals(ApiValidationStatus.PASSED, test.uploadingMeta.getApiValidationStatus())),
                                "Тест ApiValidationStatus после загрузки"}
                }
        ));
        tests.addAll(getItemsTests());
        return tests;
    }

    private static Consumer<UploadCustomListItemsTest> c(Consumer<UploadCustomListItemsTest> x) {
        return x;
    }
}
