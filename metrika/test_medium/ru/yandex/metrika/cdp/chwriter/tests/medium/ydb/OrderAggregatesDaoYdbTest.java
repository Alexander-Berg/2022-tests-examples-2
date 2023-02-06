package ru.yandex.metrika.cdp.chwriter.tests.medium.ydb;

import java.util.List;
import java.util.Map;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;
import org.springframework.test.context.web.WebAppConfiguration;

import ru.yandex.metrika.cdp.chwriter.processor.OrderAggregatesDaoYdb;
import ru.yandex.metrika.cdp.chwriter.spring.CdpChWriterTestConfig;
import ru.yandex.metrika.cdp.chwriter.tests.medium.AbstractCdpChWriterTest;
import ru.yandex.metrika.cdp.chwriter.tests.medium.CdpChWriterTestStateHolder;
import ru.yandex.metrika.cdp.dto.core.Client;
import ru.yandex.metrika.cdp.dto.core.Order;
import ru.yandex.metrika.cdp.dto.schema.OrderStatus;
import ru.yandex.metrika.util.collections.Lists2;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasEntry;
import static org.hamcrest.Matchers.hasSize;


@RunWith(SpringRunner.class)
@WebAppConfiguration
@ContextConfiguration(classes = CdpChWriterTestConfig.class)
public class OrderAggregatesDaoYdbTest extends AbstractCdpChWriterTest {

    @Autowired
    protected OrderAggregatesDaoYdb orderAggregatesDaoYdb;

    // drop all spam orders
    @Test
    public void doesntCountSpamOrders() {
        List<OrderStatus> orderStatuses = List.of(ORDER_STATUS_1, PAID_ORDER_STATUS_1, SPAM_ORDER_STATUS_1, SPAM_ORDER_STATUS_2, SPAM_ORDER_STATUS_3);
        List<Order> orders = List.of(ORDER_1, PAID_ORDER_1, SPAM_ORDER_1, SPAM_ORDER_2, SPAM_ORDER_3);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expected = testData.getOrderAggregates(CLIENT_KEY_1);

        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates, hasEntry(CLIENT_KEY_1, expected));
    }

    // tests for sum revenue
    @Test
    public void singlePaidOrderSumRevenueTest() {
        List<OrderStatus> orderStatuses = List.of(PAID_ORDER_STATUS_1);
        List<Order> orders = List.of(PAID_ORDER_1);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expected = testData.getSumRevenue(CLIENT_KEY_1);

        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getSumRevenue(), equalTo(expected));
    }

    @Test
    public void coupleOrdersSumRevenueTest() {
        List<OrderStatus> orderStatuses = List.of(ORDER_STATUS_1, PAID_ORDER_STATUS_1, CANCELLED_ORDER_STATUS);
        List<Order> orders = List.of(ORDER_1, PAID_ORDER_1, CANCELLED_ORDER);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expected = testData.getSumRevenue(CLIENT_KEY_1);

        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getSumRevenue(), equalTo(expected));
    }

    @Test
    public void noPaidOrdersSumRevenueTest() {
        List<OrderStatus> orderStatuses = List.of(ORDER_STATUS_1, CANCELLED_ORDER_STATUS);
        List<Order> orders = List.of(ORDER_1, CANCELLED_ORDER);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expected = testData.getSumRevenue(CLIENT_KEY_1);

        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getSumRevenue(), equalTo(expected));
    }

    // ltv tests
    @Test
    public void singlePaidOrderLtvTest() {
        List<OrderStatus> orderStatuses = List.of(PAID_ORDER_STATUS_1);
        List<Order> orders = List.of(PAID_ORDER_1);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expected = testData.getLtv(CLIENT_KEY_1);

        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getLtv(), equalTo(expected));
    }

    @Test
    public void coupleOrdersLtvTest() {
        List<OrderStatus> orderStatuses = List.of(ORDER_STATUS_1, PAID_ORDER_STATUS_1, CANCELLED_ORDER_STATUS);
        List<Order> orders = List.of(ORDER_1, PAID_ORDER_1, CANCELLED_ORDER);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expected = testData.getLtv(CLIENT_KEY_1);

        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getLtv(), equalTo(expected));
    }

    @Test
    public void noPaidOrdersLtvTest() {
        List<OrderStatus> orderStatuses = List.of(ORDER_STATUS_1, CANCELLED_ORDER_STATUS);
        List<Order> orders = List.of(ORDER_1, CANCELLED_ORDER);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expected = testData.getLtv(CLIENT_KEY_1);

        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getLtv(), equalTo(expected));
    }

    // create time tests
    @Test
    public void orderCreateTimeTest() {
        List<OrderStatus> orderStatuses = List.of(ORDER_STATUS_1, PAID_ORDER_STATUS_1, CANCELLED_ORDER_STATUS);
        List<Order> orders = List.of(ORDER_1, PAID_ORDER_1, CANCELLED_ORDER);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expectedFirstOrderCreate = testData.getFirstOrderCreate(CLIENT_KEY_1);
        var expectedLastOrderCreate = testData.getLastOrderCreate(CLIENT_KEY_1);


        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getFirstOrderCreateTime(), equalTo(expectedFirstOrderCreate));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getLastOrderCreateTime(), equalTo(expectedLastOrderCreate));
    }

    // finish time tests
    @Test
    public void singlePaidOrderFinishTimeTest() {
        List<OrderStatus> orderStatuses = List.of(PAID_ORDER_STATUS_1);
        List<Order> orders = List.of(PAID_ORDER_1);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expectedFirstOrderFinishTime = testData.getFirstOrderFinish(CLIENT_KEY_1);
        var expectedLastOrderFinishTime = testData.getLastOrderFinish(CLIENT_KEY_1);


        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getLastOrderFinishTime(), equalTo(expectedFirstOrderFinishTime));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getFirstOrderFinishTime(), equalTo(expectedLastOrderFinishTime));
    }

    @Test
    public void coupleOrdersFinishTimeTest() {
        List<OrderStatus> orderStatuses = List.of(ORDER_STATUS_1, PAID_ORDER_STATUS_1, CANCELLED_ORDER_STATUS);
        List<Order> orders = List.of(ORDER_1, PAID_ORDER_1, CANCELLED_ORDER);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expectedLastOrderFinishTime = testData.getLastOrderFinish(CLIENT_KEY_1);
        var expectedFirstOrderFinishTime = testData.getFirstOrderFinish(CLIENT_KEY_1);

        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getLastOrderFinishTime(), equalTo(expectedLastOrderFinishTime));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getFirstOrderFinishTime(), equalTo(expectedFirstOrderFinishTime));
    }

    @Test
    public void singlePaidOrderFinishTimeWithNullFinishDateTest() {
        List<OrderStatus> orderStatuses = List.of(PAID_ORDER_STATUS_1, PAID_ORDER_STATUS_2);
        List<Order> orders = List.of(PAID_ORDER_WITH_NULL_FINISH_DATE_1, PAID_ORDER_WITH_NULL_FINISH_DATE_2);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expectedLastOrderFinishTime = testData.getLastOrderFinish(CLIENT_KEY_1);
        var expectedFirstOrderFinishTime = testData.getFirstOrderFinish(CLIENT_KEY_1);

        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getLastOrderFinishTime(), equalTo(expectedLastOrderFinishTime));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getFirstOrderFinishTime(), equalTo(expectedFirstOrderFinishTime));
    }

    @Test
    public void singlePaidOrderFinishTimeWithNullFinishAndUpdateDateTest() {
        List<OrderStatus> orderStatuses = List.of(PAID_ORDER_STATUS_1);
        List<Order> orders = List.of(PAID_ORDER_WITH_NULL_FINISH_AND_UPDATE_DATE_1);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expectedLastOrderFinishTime = testData.getLastOrderFinish(CLIENT_KEY_1);
        var expectedFirstOrderFinishTime = testData.getFirstOrderFinish(CLIENT_KEY_1);

        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getLastOrderFinishTime(), equalTo(expectedLastOrderFinishTime));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getFirstOrderFinishTime(), equalTo(expectedFirstOrderFinishTime));
    }

    // completed count tests
    @Test
    public void countPaidAsCompletedOrderTest() {
        List<OrderStatus> orderStatuses = List.of(ORDER_STATUS_1, PAID_ORDER_STATUS_1, ORDER_STATUS_2);
        List<Order> orders = List.of(ORDER_1, PAID_ORDER_1, ORDER_2);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expected = testData.getCompletedOrdersCount(CLIENT_KEY_1);

        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getCompletedOrders(), equalTo(expected));
    }

    @Test
    public void countCancelledAsCompletedOrderTest() {
        List<OrderStatus> orderStatuses = List.of(ORDER_STATUS_1, CANCELLED_ORDER_STATUS, ORDER_STATUS_2);
        List<Order> orders = List.of(ORDER_1, CANCELLED_ORDER, ORDER_2);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expected = testData.getCompletedOrdersCount(CLIENT_KEY_1);

        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getCompletedOrders(), equalTo(expected));
    }

    @Test
    public void countCompletedOrderTest() {
        List<OrderStatus> orderStatuses = List.of(ORDER_STATUS_1, CANCELLED_ORDER_STATUS, ORDER_STATUS_2, PAID_ORDER_STATUS_1);
        List<Order> orders = List.of(ORDER_1, CANCELLED_ORDER, ORDER_2, PAID_ORDER_1);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expected = testData.getCompletedOrdersCount(CLIENT_KEY_1);

        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getCompletedOrders(), equalTo(expected));
    }

    // count paid order tests
    @Test
    public void countSinglePaidOrderTest() {
        List<OrderStatus> orderStatuses = List.of(PAID_ORDER_STATUS_1);
        List<Order> orders = List.of(PAID_ORDER_1);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expected = testData.getPaidOrdersCount(CLIENT_KEY_1);

        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getPaidOrders(), equalTo(expected));
    }

    @Test
    public void countCouplePaidOrderTest() {
        List<OrderStatus> orderStatuses = List.of(ORDER_STATUS_1, PAID_ORDER_STATUS_1, CANCELLED_ORDER_STATUS, PAID_ORDER_STATUS_2);
        List<Order> orders = List.of(ORDER_1, PAID_ORDER_1, CANCELLED_ORDER, PAID_ORDER_2);

        var testData = prepareTestData(List.of(CLIENT_1), orders, Map.of(COUNTER_ID_1, orderStatuses));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1)).join();
        var expected = testData.getPaidOrdersCount(CLIENT_KEY_1);

        assertThat(orderAggregates.entrySet(), hasSize(1));
        assertThat(orderAggregates.get(CLIENT_KEY_1).getPaidOrders(), equalTo(expected));
    }

    // couple client keys tests
    @Test
    public void coupleClientKeyTest() {
        List<OrderStatus> orderStatuses1 = List.of(ORDER_STATUS_1, PAID_ORDER_STATUS_1, CANCELLED_ORDER_STATUS);
        List<Order> orders1 = List.of(ORDER_1, PAID_ORDER_1, CANCELLED_ORDER);

        List<OrderStatus> orderStatuses2 = List.of(ORDER_STATUS_3, ORDER_STATUS_4);
        List<Order> orders2 = List.of(ORDER_3, ORDER_4);

        var testData = prepareTestData(List.of(CLIENT_1, CLIENT_2), Lists2.concat(orders1, orders2), Map.of(COUNTER_ID_1, orderStatuses1, COUNTER_ID_2, orderStatuses2));

        var orderAggregates = orderAggregatesDaoYdb.getAggregatesAsync(List.of(CLIENT_KEY_1, CLIENT_KEY_2)).join();
        var expected1 = testData.getOrderAggregates(CLIENT_KEY_1);
        var expected2 = testData.getOrderAggregates(CLIENT_KEY_2);

        assertThat(orderAggregates.entrySet(), hasSize(2));
        assertThat(orderAggregates, allOf(hasEntry(CLIENT_KEY_1, expected1), hasEntry(CLIENT_KEY_2, expected2)));
    }


    private CdpChWriterTestStateHolder prepareTestData(List<Client> clients, List<Order> orders, Map<Integer, List<OrderStatus>> orderStatuses) {
        var testData = new CdpChWriterTestStateHolder();
        testData.setClients(clients);
        testData.setOrders(orders);
        testData.setOrderStatuses(orderStatuses);

        prepareTestData(testData);

        return testData;
    }

}
