package ru.yandex.taxi.ququmber;

import java.util.Date;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ThreadLocalRandom;

import org.json.JSONObject;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;

import ru.yandex.market.checkout.checkouter.event.OrderHistoryEvent;
import ru.yandex.market.checkout.checkouter.order.Buyer;
import ru.yandex.market.checkout.checkouter.order.Order;
import ru.yandex.market.checkout.checkouter.order.OrderStatus;
import ru.yandex.market.javaframework.main.config.SpringApplicationConfig;
import ru.yandex.taxi.ququmber.clients.saas.SaasIndexingClient;
import ru.yandex.taxi.ququmber.search.OrderIndex;
import ru.yandex.taxi.ququmber.search.SearchStreamConsumerProcessor;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

@SpringBootTest(
        classes = {SpringApplicationConfig.class, TestConfiguration.class}
)
public class SearchIndexConsumerTest {

    private final static Logger log = LoggerFactory.getLogger(SearchIndexConsumerTest.class);

    @Autowired
    private SearchStreamConsumerProcessor searchStreamConsumerProcessor;

    @Autowired
    private CheckoutDeepCopyUtil copyUtil;

    @MockBean
    private SaasIndexingClient saasIndexingClient;

    @Test
    public void testIndexing() throws ExecutionException, InterruptedException {
        Date now = new Date();
        OrderHistoryEvent event = fakeOrderHistoryEvent();
        event.setToDate(now);
        event.getOrderBefore().setId(1L);
        event.getOrderBefore().setStatus(OrderStatus.RESERVED);
        event.getOrderAfter().setId(1L);
        event.getOrderAfter().setStatus(OrderStatus.PENDING);
        CompletableFuture<Void> future1 = searchStreamConsumerProcessor.processEvent(event);

        // Проверяем что в индексацию попадет только последнее событие с одинаковым timestamp
        event = fakeOrderHistoryEvent();
        event.setToDate(now);
        event.getOrderBefore().setId(1L);
        event.getOrderBefore().setStatus(OrderStatus.PENDING);
        event.getOrderAfter().setId(1L);
        event.getOrderAfter().setStatus(OrderStatus.DELIVERY);
        CompletableFuture<Void> future2 = searchStreamConsumerProcessor.processEvent(event);

        log.info("Wait for future " + future1);
        future1.get();
        future2.get();

        ArgumentCaptor<OrderIndex> argumentCaptor = ArgumentCaptor.forClass(OrderIndex.class);
        verify(saasIndexingClient, times(1)).sendToIndexing(argumentCaptor.capture());

        OrderIndex doc = argumentCaptor.getValue();
        Assertions.assertEquals("buyer@example.com", doc.buyerEmail);
        Assertions.assertEquals("DELIVERY", doc.status);
    }

    @Test
    public void testSkipIndexing() throws ExecutionException, InterruptedException {
        OrderHistoryEvent event = fakeOrderHistoryEvent();
        searchStreamConsumerProcessor.processEvent(event).get();
        // no changes - no indexing
        verify(saasIndexingClient, times(0)).sendToIndexing(any());
    }

    private OrderHistoryEvent fakeOrderHistoryEvent() {
        OrderHistoryEvent event = new OrderHistoryEvent();
        event.setToDate(new Date());
        Order order = fakeOrder();
        event.setOrderBefore(copyUtil.deepCopy(order));
        event.setOrderAfter(copyUtil.deepCopy(order));
        return event;
    }

    private Order fakeOrder() {
        Order o = new Order();
        o.setId(ThreadLocalRandom.current().nextLong(100));
        o.setStatus(OrderStatus.PLACING);
        o.setBuyer(fakeBuyer());
        Date date = new Date();
        o.setCreationDate(date);
        o.setUpdateDate(date);
        return o;
    }

    private Buyer fakeBuyer() {
        Buyer b = new Buyer();
        b.setUid(ThreadLocalRandom.current().nextLong(100));
        b.setEmail("buyer@example.com");
        b.setFirstName("Иван");
        b.setMiddleName("Петрович");
        b.setLastName("Сергеев");
        b.setPhone("+79991234567");
        return b;
    }

}
