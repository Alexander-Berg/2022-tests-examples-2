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
import ru.yandex.metrika.cdp.dto.core.OrderUpdate;
import ru.yandex.metrika.cdp.dto.core.UpdateType;
import ru.yandex.metrika.cdp.dto.schema.EntityNamespace;
import ru.yandex.metrika.cdp.dto.uploading.UploadingFormat;
import ru.yandex.metrika.cdp.frontend.data.CSVColumnNames;
import ru.yandex.metrika.cdp.frontend.data.DelimiterType;
import ru.yandex.metrika.cdp.frontend.data.rows.OrderRow;
import ru.yandex.metrika.util.io.IOUtils;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractDataServiceTest.DataConfig.class})
public class CreateUploadOrdersCsvTest extends AbstractDataServiceTest {


    List<OrderUpdate> ordersFromFile;
    OrderUpdate firstOrderUpdateFromLb;
    OrderUpdate secondOrderUpdateFromLb;

    @Before
    public void testBody() {
        int counterId = getCounterId();
        byte[] fileContent = IOUtils
                .resourceAsString(CreateUploadContactsCsvTest.class, "./csv/test_orders.csv").getBytes();
        MultipartFile multipartFileWithOrders = new MockMultipartFile("Orders.csv", fileContent);
        CSVColumnNames orderMapping = new CSVColumnNames(ORDER_COLUMNS_MAPPING);
        counterBefore = cdpCountersDao.getCounter(counterId);

        hasFeatureBefore = featureService.getFeatures(counterId).contains(Feature.cdp);

        uploadingMeta = dataService.uploadOrdersCsv(
                counterId,
                UpdateType.APPEND,
                orderMapping,
                DelimiterType.SEMICOLON,
                multipartFileWithOrders
        );

        ordersFromFile = parseUpdateRows(orderMapping,
                multipartFileWithOrders,
                EntityNamespace.ORDER,
                OrderRow.class,
                uploadingMeta.getUploadingId(),
                uploadingMeta.getUpdateType());
        var clientsFromLb = readEntityFromLb(ordersSyncConsumer,
                orderUpdateProtoSerializer,
                uploadingMeta.getUploadingId(),
                2);
        firstOrderUpdateFromLb = clientsFromLb.get(0);
        secondOrderUpdateFromLb = clientsFromLb.get(1);
        counter = cdpCountersDao.getCounter(counterId);

        hasFeature = featureService.getFeatures(counterId).contains(Feature.cdp);
    }

    @Parameterized.Parameters(name = "{1}")
    public static List<Object[]> getParameters() {
        var result = new ArrayList<>(
                Arrays.asList(
                        new Object[][]{
                                {c(test -> assertEquals(Integer.valueOf(2), test.uploadingMeta.getElementsCount())),
                                        "Тест количества загруженных заказов"},
                                {c(test -> assertEquals(UploadingFormat.CSV, test.uploadingMeta.getUploadingFormat())),
                                        "Тест формата загруженных данных"},
                                {c(test -> assertNotNull(test.firstOrderUpdateFromLb)),
                                        "Проверка не nullability первого загруженного заказа"},
                                {c(test -> assertEqualUpdates(test.firstOrderUpdateFromLb, test.ordersFromFile.get(0))),
                                        "Тест первого загруженного заказа"},
                                {c(test -> assertNotNull(test.secondOrderUpdateFromLb)),
                                        "Проверка не nullability второго загруженного заказа"},
                                {c(test -> assertEqualUpdates(test.secondOrderUpdateFromLb, test.ordersFromFile.get(1))),
                                        "Тест второго загруженного заказа"},
                                {c(test -> assertEquals((Long) 100L, test.counter.getCdpOrderInProgressGoalId())),
                                        "Тест cdpOrderInProgressGoalId"},
                                {c(test -> assertEquals((Long) 200L, test.counter.getCdpOrderPaidGoalId())),
                                        "Тест cdpOrderPaidGoalId"},
                                {c(test -> assertFalse(test.counter.isHasContacts())), "Тест отсутствия контактов у счётчика"},
                                {c(test -> assertTrue(test.counter.isHasOrders())), "Тест наличия заказов у счётчика"},
                                {c(test -> assertTrue(test.counter.isHasProducts())), "Тест наличия продуктов у счётчика"}
                        }
                ));
        result.addAll(getCommonParameters());
        return result;
    }

    private static Consumer<CreateUploadOrdersCsvTest> c(Consumer<CreateUploadOrdersCsvTest> x) {
        return x;
    }
}
