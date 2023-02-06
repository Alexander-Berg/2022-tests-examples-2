package ru.yandex.metrika.cdp.api.tests.medium.service.dataservice;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.function.Consumer;

import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.test.context.ContextConfiguration;

import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.cdp.api.validation.builders.OrderRowBuilder;
import ru.yandex.metrika.cdp.dto.core.ClientType;
import ru.yandex.metrika.cdp.dto.core.OrderUpdate;
import ru.yandex.metrika.cdp.dto.core.UpdateType;
import ru.yandex.metrika.cdp.dto.uploading.UploadingFormat;
import ru.yandex.metrika.cdp.frontend.data.rows.OrderRow;
import ru.yandex.metrika.cdp.frontend.data.wrappers.OrderRowsListWrapper;
import ru.yandex.metrika.cdp.frontend.rows.RowsTestUtils;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractDataServiceTest.DataConfig.class})
public class CreateUploadOrdersJsonTest extends AbstractDataServiceTest {

    OrderRow orderRow;
    OrderUpdate orderUpdateFromLb;

    @Before
    public void testBody() {
        int counterId = getCounterId();
        counterBefore = cdpCountersDao.getCounter(counterId);
        orderRow = OrderRowBuilder.anOrderRow()
                .withId("32152")
                .withClientUniqId("some345textId")
                .withClientType(ClientType.CONTACT)
                .withCreateDateTime(LocalDateTime.now())
                .withRevenue(BigDecimal.valueOf(1000.123))
                .withOrderStatus("создан")
                .withCost(BigDecimal.valueOf(1000))
                .build();

        hasFeatureBefore = featureService.getFeatures(counterId).contains(Feature.cdp);

        uploadingMeta = dataService
                .uploadOrdersJson(counterId, UpdateType.APPEND, new OrderRowsListWrapper(List.of(orderRow)));

        orderUpdateFromLb = readEntityFromLb(ordersSyncConsumer, orderUpdateProtoSerializer,
                uploadingMeta.getUploadingId(), 1).get(0);
        counter = cdpCountersDao.getCounter(counterId);
        hasFeature = featureService.getFeatures(counterId).contains(Feature.cdp);
    }

    @Parameterized.Parameters(name = "{1}")
    public static List<Object[]> getParameters() {
        var result = new ArrayList<>(
                Arrays.asList(
                        new Object[][]{
                                {c(test -> assertEquals(Integer.valueOf(1), test.uploadingMeta.getElementsCount())),
                                        "Тест количества загруженных заказов"},
                                {c(test -> assertEquals(UploadingFormat.JSON, test.uploadingMeta.getUploadingFormat())),
                                        "Тест формата загруженных данных"},
                                {c(test -> assertNotNull(test.orderUpdateFromLb)), "Тест не nullability загруженного заказа"},
                                {c(test -> assertEqualUpdates(
                                        test.orderUpdateFromLb,
                                        RowsTestUtils.getEntityUpdate(test.orderRow,
                                                test.uploadingMeta.getUploadingId(),
                                                test.uploadingMeta.getUpdateType(),
                                                1
                                        ))),
                                        "Тест загруженного заказа"},
                                {c(test -> assertEquals((Long) 100L, test.counter.getCdpOrderInProgressGoalId())),
                                        "Тест cdpOrderInProgressGoalId"},
                                {c(test -> assertEquals((Long) 200L, test.counter.getCdpOrderPaidGoalId())),
                                        "Тест cdpOrderPaidGoalId"},
                                {c(test -> assertFalse(test.counter.isHasContacts())), "Тест отсутствия контактов у счётчика"},
                                {c(test -> assertTrue(test.counter.isHasOrders())), "Тест наличия заказов у счётчика"},
                                {c(test -> assertFalse(test.counter.isHasProducts())), "Тест наличия продуктов у счётчика"}
                        }));
        result.addAll(getCommonParameters());
        return result;
    }

    private static Consumer<CreateUploadOrdersJsonTest> c(Consumer<CreateUploadOrdersJsonTest> x) {
        return x;
    }
}
