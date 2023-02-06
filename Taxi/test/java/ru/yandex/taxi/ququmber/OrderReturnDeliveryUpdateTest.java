package ru.yandex.taxi.ququmber;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.mockito.ArgumentCaptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;

import ru.yandex.market.checkout.checkouter.client.CheckouterAPI;
import ru.yandex.market.checkout.checkouter.client.CheckouterReturnApi;
import ru.yandex.market.checkout.checkouter.event.HistoryEventType;
import ru.yandex.market.checkout.checkouter.event.OrderHistoryEvent;
import ru.yandex.market.checkout.checkouter.order.Buyer;
import ru.yandex.market.checkout.checkouter.order.Order;
import ru.yandex.market.checkout.checkouter.order.OrderItem;
import ru.yandex.market.checkout.checkouter.order.OrderStatus;
import ru.yandex.market.checkout.checkouter.order.SupplierType;
import ru.yandex.market.checkout.checkouter.returns.Return;
import ru.yandex.market.checkout.checkouter.returns.ReturnDelivery;
import ru.yandex.market.checkout.checkouter.returns.ReturnDeliveryStatus;
import ru.yandex.market.javaframework.main.config.SpringApplicationConfig;
import ru.yandex.startrek.client.StartrekClient;
import ru.yandex.taxi.ququmber.clients.chatterbox.ChatterboxClient;
import ru.yandex.taxi.ququmber.tickets.TicketStreamConsumerProcessor;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.only;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@SpringBootTest(
        classes = {SpringApplicationConfig.class, TestConfiguration.class}
)
public class OrderReturnDeliveryUpdateTest {

    @Autowired
    TicketStreamConsumerProcessor ticketStreamConsumerProcessor;

    @MockBean
    StartrekClient startrekClient;

    @MockBean
    ChatterboxClient chatterboxClient;

    @Autowired
    CheckouterAPI checkouterAPI;

    @ParameterizedTest
    @CsvSource({
            "DELIVERED, true",
            "DELIVERY, false",
            "EXPIRED, true",
    })
    public void testTicketProcessing(String status, boolean callCbox) {

        OrderHistoryEvent event = new OrderHistoryEvent();
        event.setReturnId(25L);
        event.setOrderAfter(fakeOrder());
        event.getOrderAfter().setId(40L);
        event.setType(HistoryEventType.ORDER_RETURN_DELIVERY_STATUS_UPDATED);

        CheckouterReturnApi returns = mock(CheckouterReturnApi.class);
        when(checkouterAPI.returns()).thenReturn(returns);

        Return ret = new Return();
        ret.setDelivery(new ReturnDelivery());
        ret.getDelivery().setStatus(ReturnDeliveryStatus.valueOf(status));
        when(returns.getReturn(any(), any())).thenReturn(ret);

        ticketStreamConsumerProcessor.processOrderHistoryEvent(event);

        if (callCbox) {
            ArgumentCaptor<Long> orderIdCaptor = ArgumentCaptor.forClass(Long.class);
            ArgumentCaptor<Long> returnIdCaptor = ArgumentCaptor.forClass(Long.class);
            verify(chatterboxClient, only()).orderReturnUpdated(orderIdCaptor.capture(), returnIdCaptor.capture());

            Assertions.assertEquals(40L, orderIdCaptor.getValue());
            Assertions.assertEquals(25L, returnIdCaptor.getValue());
        } else {
            verify(chatterboxClient, never()).orderReturnUpdated(anyLong(), anyLong());
        }

    }

    public Order fakeOrder() {
        Order o = new Order();
        o.setId(ThreadLocalRandom.current().nextLong(100));
        o.setStatus(OrderStatus.DELIVERY);
        o.setBuyer(fakeBuyer());
        Date date = new Date();
        o.setCreationDate(date);
        o.setUpdateDate(date);
        List<OrderItem> items = new ArrayList<>();
        OrderItem item1 = new OrderItem();
        item1.setId(1L);
        item1.setSupplierType(SupplierType.THIRD_PARTY);
        items.add(item1);
        o.setItems(items);
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
}
