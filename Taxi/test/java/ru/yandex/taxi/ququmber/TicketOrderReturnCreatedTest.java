package ru.yandex.taxi.ququmber;

import java.util.Date;
import java.util.concurrent.ThreadLocalRandom;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;

import ru.yandex.bolts.collection.impl.EmptyMap;
import ru.yandex.market.checkout.checkouter.event.HistoryEventType;
import ru.yandex.market.checkout.checkouter.event.OrderHistoryEvent;
import ru.yandex.market.checkout.checkouter.order.Buyer;
import ru.yandex.market.checkout.checkouter.order.Order;
import ru.yandex.market.checkout.checkouter.order.OrderStatus;
import ru.yandex.market.javaframework.main.config.SpringApplicationConfig;
import ru.yandex.startrek.client.Issues;
import ru.yandex.startrek.client.StartrekClient;
import ru.yandex.startrek.client.model.Issue;
import ru.yandex.startrek.client.model.IssueCreate;
import ru.yandex.taxi.ququmber.tickets.TicketStreamConsumerProcessor;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@SpringBootTest(
        classes = {SpringApplicationConfig.class, TestConfiguration.class}
)
public class TicketOrderReturnCreatedTest {

    private final static Logger log = LoggerFactory.getLogger(TicketOrderReturnCreatedTest.class);

    @Autowired
    private TicketStreamConsumerProcessor ticketStreamConsumerProcessor;

    @Autowired
    private CheckoutDeepCopyUtil copyUtil;

    @MockBean
    private StartrekClient startrekClient;

    @Test
    public void testTicketProcessing() {

        OrderHistoryEvent event = fakeOrderHistoryEvent();
        event.setOrderBefore(null);
        event.setReturnId(25L);
        event.getOrderAfter().setId(40L);
        event.setType(HistoryEventType.ORDER_RETURN_CREATED);

        Issues issues = mock(Issues.class);
        when(startrekClient.issues(any())).thenReturn(issues);

        ArgumentCaptor<IssueCreate> argumentCaptor = ArgumentCaptor.forClass(IssueCreate.class);
        when(issues.create(argumentCaptor.capture())).thenReturn(fakeIssue()).thenThrow(new IllegalStateException());

        ticketStreamConsumerProcessor.processOrderHistoryEvent(event);

        IssueCreate issueCreate = argumentCaptor.getValue();
        Assertions.assertEquals("Возврат Маркета 25, заказ 40", issueCreate.getValues().getOrThrow("summary"));
        Assertions.assertEquals(25L, issueCreate.getValues().getOrThrow("OrderReturnId"));
        Assertions.assertEquals(40L, issueCreate.getValues().getOrThrow("OrderId"));
        Assertions.assertEquals("cbox@example.com", issueCreate.getValues().getOrThrow("emailCreatedBy"));
        Assertions.assertEquals("TRACKER_QUEUE", issueCreate.getValues().getOrThrow("queue"));
        Assertions.assertEquals("возврат", ((String[])issueCreate.getValues().getOrThrow("tags"))[0]);
    }

    public OrderHistoryEvent fakeOrderHistoryEvent() {
        OrderHistoryEvent event = new OrderHistoryEvent();
        Order order = fakeOrder();
        event.setOrderBefore(copyUtil.deepCopy(order));
        event.setOrderAfter(copyUtil.deepCopy(order));
        return event;
    }

    public Order fakeOrder() {
        Order o = new Order();
        o.setId(ThreadLocalRandom.current().nextLong(100));
        o.setStatus(OrderStatus.PLACING);
        o.setBuyer(fakeBuyer());
        Date date = new Date();
        o.setCreationDate(date);
        o.setUpdateDate(date);
        return o;
    }

    public Buyer fakeBuyer() {
        Buyer b = new Buyer();
        b.setUid(ThreadLocalRandom.current().nextLong(100));
        b.setEmail("buyer@example.com");
        b.setFirstName("Иван");
        b.setMiddleName("Петрович");
        b.setLastName("Сергеев");
        b.setPhone("+79991234567");
        return b;
    }

    private Issue fakeIssue() {
        return new Issue("id1", null, "TRACKER_QUEUE-1", "summary", 1L, new EmptyMap<>(), null);
    }
}
