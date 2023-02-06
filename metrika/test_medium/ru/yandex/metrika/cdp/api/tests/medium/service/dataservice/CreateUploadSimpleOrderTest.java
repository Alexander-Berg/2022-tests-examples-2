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
import ru.yandex.metrika.cdp.dto.core.SimpleOrderUpdate;
import ru.yandex.metrika.cdp.dto.core.UpdateType;
import ru.yandex.metrika.cdp.dto.schema.EntityNamespace;
import ru.yandex.metrika.cdp.dto.uploading.UploadingFormat;
import ru.yandex.metrika.cdp.frontend.data.DelimiterType;
import ru.yandex.metrika.cdp.frontend.data.rows.SimpleOrderRow;
import ru.yandex.metrika.util.io.IOUtils;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;
import static ru.yandex.metrika.cdp.frontend.data.DataService.DEFAULT_SIMPLE_COLUMN_NAME;

@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractDataServiceTest.DataConfig.class})
public class CreateUploadSimpleOrderTest extends AbstractDataServiceTest {
    List<SimpleOrderUpdate> simpleOrdersFromFile;
    OrderUpdate firstOrderUpdateFromLb;
    OrderUpdate secondOrderUpdateFromLb;

    @Before
    public void testBody() {
        int counterId = getCounterId();
        byte[] fileContent = IOUtils
                .resourceAsString(CreateUploadContactsCsvTest.class, "./csv/test_simple_orders.csv").getBytes();
        MultipartFile multipartFileWithOrders = new MockMultipartFile("Simple_Orders.csv", fileContent);
        counterBefore = cdpCountersDao.getCounter(counterId);

        hasFeatureBefore = featureService.getFeatures(counterId).contains(Feature.cdp);

        uploadingMeta = dataService.uploadSimpleOrdersCsv(
                counterId,
                UpdateType.APPEND,
                DelimiterType.SEMICOLON,
                multipartFileWithOrders
        );

        simpleOrdersFromFile = parseUpdateRows(DEFAULT_SIMPLE_COLUMN_NAME,
                multipartFileWithOrders,
                EntityNamespace.SIMPLE_ORDER,
                SimpleOrderRow.class,
                uploadingMeta.getUploadingId(),
                uploadingMeta.getUpdateType());

        var orders = readEntityFromLb(ordersSyncConsumer,
                orderUpdateProtoSerializer,
                uploadingMeta.getUploadingId(),
                3);

        firstOrderUpdateFromLb = orders.get(0);
        secondOrderUpdateFromLb = orders.get(1);
        counter = cdpCountersDao.getCounter(counterId);

        hasFeature = featureService.getFeatures(counterId).contains(Feature.cdp);
    }

    @Parameterized.Parameters(name = "{1}")
    public static List<Object[]> getParameters() {
        var result = new ArrayList<>(
                Arrays.asList(
                        new Object[][]{
                                {c(test -> assertEquals(Integer.valueOf(3), test.uploadingMeta.getElementsCount())),
                                        "Тест количества загруженных заказов"},
                                {c(test -> assertEquals(UploadingFormat.CSV, test.uploadingMeta.getUploadingFormat())),
                                        "Тест формата загруженных данных"},
                                {c(test -> assertNotNull(test.firstOrderUpdateFromLb)),
                                        "Проверка не nullability первого загруженного заказа"},
                                {c(test -> assertEqualUpdates(test.firstOrderUpdateFromLb, test.simpleOrdersFromFile.get(0).getOrderUpdate())),
                                        "Тест первого загруженного заказа"},
                                {c(test -> assertNotNull(test.secondOrderUpdateFromLb)),
                                        "Проверка не nullability второго загруженного заказа"},
                                {c(test -> assertEqualUpdates(test.secondOrderUpdateFromLb, test.simpleOrdersFromFile.get(1).getOrderUpdate())),
                                        "Тест второго загруженного заказа"},
                                {c(test -> assertEquals((Long) 100L, test.counter.getCdpOrderInProgressGoalId())),
                                        "Тест cdpOrderInProgressGoalId"},
                                {c(test -> assertEquals((Long) 200L, test.counter.getCdpOrderPaidGoalId())),
                                        "Тест cdpOrderPaidGoalId"},
                                {c(test -> assertTrue(test.counter.isHasContacts())), "Тест отсутствия контактов у счётчика"},
                                {c(test -> assertTrue(test.counter.isHasOrders())), "Тест наличия заказов у счётчика"},
                                {c(test -> assertFalse(test.counter.isHasProducts())), "Тест наличия продуктов у счётчика"}
                        }
                ));
        result.addAll(getCommonParameters());
        return result;
    }

    private static Consumer<CreateUploadSimpleOrderTest> c(Consumer<CreateUploadSimpleOrderTest> x) {
        return x;
    }
}
