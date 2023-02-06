package ru.yandex.metrika.cdp.api.tests.medium.service.schemaservice;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.test.context.ContextConfiguration;

import ru.yandex.metrika.cdp.dto.schema.OrderStatus;
import ru.yandex.metrika.cdp.dto.schema.OrderStatusType;

import static java.util.stream.Collectors.toMap;
import static org.junit.Assert.assertTrue;

@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractSchemaServiceTest.SchemaConfig.class})
public class SaveOrderStatusesTest extends AbstractSchemaServiceParameterizedTest {

    static final List<OrderStatus> orderStatusList = List.of(
            new OrderStatus("od1", "Статус заказа аналогичный 'В работе'", OrderStatusType.IN_PROGRESS),
            new OrderStatus("od2", "Статус заказа аналогичный 'Оплачен'", OrderStatusType.PAID),
            new OrderStatus("od3", "Статус заказа аналогичный 'Отменен'", OrderStatusType.CANCELLED),
            new OrderStatus("od4", "Статус заказа аналогичный 'Спам'", OrderStatusType.SPAM),
            new OrderStatus("od5", "Статус заказа аналогичный 'Не определен'", OrderStatusType.UNDEFINED),
            new OrderStatus("null", null, OrderStatusType.SPAM)
    );

    Map<String, OrderStatus> orderStatusesFromYDB;

    @Before
    public void testBody() {
        schemaService.saveOrderStatuses(getCounterId(), orderStatusList);
        //В schemaService нет метода для запроса статусов заказов, будем читать напрямую через SchemaDaoYdb
        orderStatusesFromYDB = schemaDao
                .getOrderStatuses(getCounterId())
                .stream()
                .collect(toMap(OrderStatus::getId, x -> x));


    }

    @Parameterized.Parameters(name = "{1}")
    public static List<Object[]> getParameters() {
        return Arrays.asList(
                new Object[][]{
                        {c(test -> assertTrue("Получено меньше статусов заказов, чем загружено в систему",
                                test.orderStatusesFromYDB.size() >= orderStatusList.size())),
                                "Тест количества загруженных статусов"},
                        {c(test -> {
                            for (var orderStatus : orderStatusList) {
                                assertTrue("expected: " + orderStatus +
                                        " but got: " + test.orderStatusesFromYDB.get(orderStatus.getId()),
                                        areOrderStatusesEquals(
                                                orderStatus,
                                                test.orderStatusesFromYDB.get(orderStatus.getId())));
                            }
                        }), "Тест корректности загруженных статусов"}
                });
    }

    static private boolean areOrderStatusesEquals(OrderStatus orderStatus, OrderStatus anotherOrderStatus) {
        if (orderStatus != null) {
            return anotherOrderStatus != null &&
                    orderStatus.getId().equals(anotherOrderStatus.getId()) &&
                    orderStatus.getType().equals(anotherOrderStatus.getType()) &&
                    ((orderStatus.getHumanized() != null && orderStatus.getHumanized().equals(anotherOrderStatus.getHumanized())) ||
                            (orderStatus.getHumanized() == null && anotherOrderStatus.getHumanized() == null));
        } else {
            return anotherOrderStatus == null;
        }
    }

    private static Consumer<SaveOrderStatusesTest> c(Consumer<SaveOrderStatusesTest> x) {
        return x;
    }
}
