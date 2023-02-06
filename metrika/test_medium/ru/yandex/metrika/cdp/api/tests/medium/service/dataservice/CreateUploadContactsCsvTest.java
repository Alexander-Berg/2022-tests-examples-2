package ru.yandex.metrika.cdp.api.tests.medium.service.dataservice;

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

import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.cdp.dto.core.ClientUpdate;
import ru.yandex.metrika.cdp.dto.core.UpdateType;
import ru.yandex.metrika.cdp.dto.schema.EntityNamespace;
import ru.yandex.metrika.cdp.dto.uploading.UploadingFormat;
import ru.yandex.metrika.cdp.frontend.data.CSVColumnNames;
import ru.yandex.metrika.cdp.frontend.data.DelimiterType;
import ru.yandex.metrika.cdp.frontend.data.rows.ContactRow;
import ru.yandex.metrika.util.io.IOUtils;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractDataServiceTest.DataConfig.class})
public class CreateUploadContactsCsvTest extends AbstractDataServiceTest {

    ClientUpdate clientUpdateFromLb;
    List<ClientUpdate> contactFromCsv;

    @Before
    public void testBody() {
        int counterId = getCounterId();
        counterBefore = cdpCountersDao.getCounter(counterId);
        byte[] fileContent = IOUtils
                .resourceAsString(CreateUploadContactsCsvTest.class, "./csv/test_contacts.csv").getBytes();
        MultipartFile multipartFileWithContacts = new MockMultipartFile("Contacts.csv", fileContent);
        CSVColumnNames contactMapping = new CSVColumnNames(CONTACT_COLUMNS_MAPPING);

        hasFeatureBefore = featureService.getFeatures(counterId).contains(Feature.cdp);

        uploadingMeta = dataService.uploadContactsCsv(
                counterId,
                UpdateType.APPEND,
                contactMapping,
                DelimiterType.SEMICOLON,
                multipartFileWithContacts
        );
        clientUpdateFromLb = readEntityFromLb(contactsSyncConsumer, clientUpdateProtoSerializer,
                uploadingMeta.getUploadingId(), 1).get(0);
        contactFromCsv = parseUpdateRows(contactMapping,
                multipartFileWithContacts,
                EntityNamespace.CONTACT,
                ContactRow.class,
                uploadingMeta.getUploadingId(),
                uploadingMeta.getUpdateType());
        counter = cdpCountersDao.getCounter(counterId);

        hasFeature = featureService.getFeatures(counterId).contains(Feature.cdp);
    }

    @Parameterized.Parameters(name = "{1}")
    public static List<Object[]> getParameters() {
        var result = new ArrayList<>(
                Arrays.asList(
                        new Object[][]{
                                {c(test -> assertEquals(Integer.valueOf(1), test.uploadingMeta.getElementsCount())),
                                        "Тест количества загруженных контактов"},
                                {c(test -> assertEquals(UploadingFormat.CSV, test.uploadingMeta.getUploadingFormat())),
                                        "Тест формата загруженных данных"},
                                {c(test -> assertNotNull(test.clientUpdateFromLb)), "Тест не nullability загруженного контакта"},
                                {c(test -> assertEqualUpdates(test.clientUpdateFromLb, test.contactFromCsv.get(0))),
                                        "Тест загруженного контакта"},
                                {c(test -> assertTrue(test.counter.isHasContacts())), "Тест наличия контактов у счётчика"},
                                {c(test -> assertFalse(test.counter.isHasOrders())), "Тест отсутствия заказов у счётчика"},
                        }
                ));
        result.addAll(getCommonParameters());
        return result;
    }

    private static Consumer<CreateUploadContactsCsvTest> c(Consumer<CreateUploadContactsCsvTest> x) {
        return x;
    }
}
