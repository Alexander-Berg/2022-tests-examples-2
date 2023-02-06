package ru.yandex.metrika.cdp.core.processing;

import java.util.UUID;

import javax.annotation.Nonnull;

import ru.yandex.metrika.cdp.dto.core.EntityStatus;
import ru.yandex.metrika.cdp.dto.core.Order;

public abstract class AbstractOrderMergerTest {

    protected static final UUID UPLOADING_ID_1 = UUID.randomUUID();
    protected static final UUID UPLOADING_ID_2 = UUID.randomUUID();
    protected static final UUID UPLOADING_ID_3 = UUID.randomUUID();

    protected final OrderMerger orderMerger = new OrderMerger(
            (counterId, entityNamespace, attributeName) -> false
    );

    @Nonnull
    protected static Order getEmptyOrder() {
        return new Order(1L, 1, 1L, "1", EntityStatus.ACTIVE, "done");
    }
}
