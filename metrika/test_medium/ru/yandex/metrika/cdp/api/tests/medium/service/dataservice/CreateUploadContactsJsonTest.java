package ru.yandex.metrika.cdp.api.tests.medium.service.dataservice;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.function.Consumer;

import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.test.context.ContextConfiguration;

import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.cdp.api.validation.builders.ContactRowBuilder;
import ru.yandex.metrika.cdp.common.CdpDateTimeUtils;
import ru.yandex.metrika.cdp.dto.core.ClientUpdate;
import ru.yandex.metrika.cdp.dto.core.UpdateType;
import ru.yandex.metrika.cdp.dto.uploading.UploadingFormat;
import ru.yandex.metrika.cdp.frontend.data.rows.ContactRow;
import ru.yandex.metrika.cdp.frontend.data.wrappers.ContactRowsListWrapper;
import ru.yandex.metrika.cdp.frontend.rows.RowsTestUtils;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractDataServiceTest.DataConfig.class})
public class CreateUploadContactsJsonTest extends AbstractDataServiceTest {

    ContactRow firstContact;
    ContactRow secondContact;
    ClientUpdate firstClientUpdateFromLb;
    ClientUpdate secondClientUpdateFromLb;

    @Before
    public void testBody() {
        int counterId = getCounterId();
        counterBefore = cdpCountersDao.getCounter(counterId);
        firstContact = ContactRowBuilder.aContactRow()
                .withUniqId("bla_bla_bla")
                .withName("Иванов Дмитрий Петрович")
                .withBirthDate(CdpDateTimeUtils.parseLocalDate("1982-09-14"))
                .withCreateDateTime(CdpDateTimeUtils.parseLocalDateTime("2020-04-30 16:12:21"))
                .withUpdateDateTime(CdpDateTimeUtils.parseLocalDateTime("2020-05-17 16:12:21"))
                .withEmails(Set.of("exampl1@example.com", "example2@example.com"))
                .withPhones(Set.of("88005553535", "83449932378"))
                .build();
        secondContact = ContactRowBuilder.aContactRow()
                .withUniqId("12424")
                .withName("Иванов Дмитрий Петрович")
                .withBirthDate(CdpDateTimeUtils.parseLocalDate("1970-10-15"))
                .withCreateDateTime(CdpDateTimeUtils.parseLocalDateTime("2020-04-02 16:12:21"))
                .withUpdateDateTime(CdpDateTimeUtils.parseLocalDateTime("2020-04-12 16:12:21"))
                .withEmails(Set.of("example3@example.com", "example4@example.com"))
                .withPhones(Set.of("83432123434", "83449932378"))
                .build();

        hasFeatureBefore = featureService.getFeatures(counterId).contains(Feature.cdp);

        uploadingMeta = dataService
                .uploadContactsJson(counterId, UpdateType.APPEND,
                        new ContactRowsListWrapper(List.of(firstContact, secondContact)));
        var clientsFromLb = readEntityFromLb(contactsSyncConsumer, clientUpdateProtoSerializer,
                uploadingMeta.getUploadingId(), 2);
        firstClientUpdateFromLb = clientsFromLb.get(0);
        secondClientUpdateFromLb = clientsFromLb.get(1);
        counter = cdpCountersDao.getCounter(counterId);

        hasFeature = featureService.getFeatures(counterId).contains(Feature.cdp);
    }

    @Parameterized.Parameters(name = "{1}")
    public static List<Object[]> getParameters() {
        var result = new ArrayList<>(
                Arrays.asList(
                        new Object[][]{
                                {c(test -> assertEquals(Integer.valueOf(2), test.uploadingMeta.getElementsCount())),
                                        "Тест количества загруженных контактов"},
                                {c(test -> assertEquals(UploadingFormat.JSON, test.uploadingMeta.getUploadingFormat())),
                                        "Тест формата загруженных данных"},
                                {c(test -> assertNotNull(test.firstClientUpdateFromLb)),
                                        "Тест не nullability первого загруженного контакта"},
                                {c(test -> assertEqualUpdates(
                                        test.firstClientUpdateFromLb,
                                        RowsTestUtils.getEntityUpdate(
                                                test.firstContact,
                                                test.uploadingMeta.getUploadingId(),
                                                test.uploadingMeta.getUpdateType(),
                                                1))),
                                        "Тест первого загруженного контакта"},
                                {c(test -> assertNotNull(test.secondClientUpdateFromLb)),
                                        "Тест не nullability второго загруженного контакта"},
                                {c(test -> assertEqualUpdates(
                                        test.secondClientUpdateFromLb,
                                        RowsTestUtils.getEntityUpdate(
                                                test.secondContact,
                                                test.uploadingMeta.getUploadingId(),
                                                test.uploadingMeta.getUpdateType(),
                                                2))),
                                        "Тест второго загруженного контакта"},
                                {c(test -> assertTrue(test.counter.isHasContacts())), "Тест наличия контактов у счётчика"},
                                {c(test -> assertFalse(test.counter.isHasOrders())), "Тест отсутствия заказов у счётчика"}
                        }
                ));
        result.addAll(getCommonParameters());
        return result;
    }

    private static Consumer<CreateUploadContactsJsonTest> c(Consumer<CreateUploadContactsJsonTest> x) {
        return x;
    }
}
