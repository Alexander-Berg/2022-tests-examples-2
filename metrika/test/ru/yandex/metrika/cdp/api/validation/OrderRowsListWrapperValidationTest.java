package ru.yandex.metrika.cdp.api.validation;

import java.time.LocalDateTime;
import java.util.List;

import org.junit.Test;

import ru.yandex.metrika.cdp.api.validation.builders.OrderRowBuilder;
import ru.yandex.metrika.cdp.api.validation.builders.OrderRowsListWrapperBuilder;
import ru.yandex.metrika.cdp.frontend.data.wrappers.OrderRowsListWrapper;

import static org.junit.Assert.assertThat;

public class OrderRowsListWrapperValidationTest extends AbstractValidationTest<OrderRowsListWrapper, OrderRowsListWrapperBuilder> {

    @Test
    public void testNullOrders() {
        var orderRowsListWrapper = minimalValidBuilder().withOrders(null).build();
        assertThat(orderRowsListWrapper, notValidAtLocation("orders"));
    }


    @Test
    public void testEmptyOrders() {
        var orderRowsListWrapper = minimalValidBuilder().withOrders(List.of()).build();
        assertThat(orderRowsListWrapper, notValidAtLocation("orders"));
    }

    @Test
    public void testSeveralErrors() {
        var orderRowListWrapper = OrderRowsListWrapperBuilder.anOrderRowsListWrapper().withOrders(
                List.of(
                        OrderRowBuilder.minimalValidBuilder()
                                .withUpdateDateTime(LocalDateTime.parse("1920-04-17T16:12:21"))
                                .build(),
                        OrderRowBuilder.minimalValidBuilder()
                                .withCreateDateTime(LocalDateTime.parse("1920-04-30T16:12:21"))
                                .build()
                )
        ).build();
        assertThat(orderRowListWrapper, notValidAtLocations(List.of("orders[0].updateDateTime", "orders[1].createDateTime")));
    }

    @Override
    protected OrderRowsListWrapperBuilder minimalValidBuilder() {
        return OrderRowsListWrapperBuilder.anOrderRowsListWrapper().withOrders(
                List.of(
                        OrderRowBuilder.minimalValidBuilder().build()
                )
        );
    }
}
