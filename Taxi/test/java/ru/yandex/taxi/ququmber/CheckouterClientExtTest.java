package ru.yandex.taxi.ququmber;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import ru.yandex.market.checkout.checkouter.client.CheckouterAPI;
import ru.yandex.market.checkout.checkouter.client.CheckouterReturnApi;
import ru.yandex.market.checkout.checkouter.returns.Return;
import ru.yandex.market.checkout.checkouter.returns.ReturnStatus;
import ru.yandex.market.javaframework.main.config.SpringApplicationConfig;
import ru.yandex.taxi.ququmber.clients.checkouter.CheckouterClientExt;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@SpringBootTest(
        classes = {SpringApplicationConfig.class, TestConfiguration.class}
)
public class CheckouterClientExtTest {

    @Autowired
    CheckouterAPI checkouterAPI;

    @Autowired
    CheckouterClientExt checkouterClientExt;

    @Test
    public void testRetry() {

        CheckouterReturnApi returns = mock(CheckouterReturnApi.class);
        when(checkouterAPI.returns()).thenReturn(returns);

        Return ret = new Return();
        ret.setStatus(ReturnStatus.STARTED_BY_USER);
        when(returns.getReturn(any(), any()))
                .thenThrow(new RuntimeException("failed get return"))
                .thenReturn(ret);

        Return loadedReturn = checkouterClientExt.loadReturn(1L, 1L);

        Assertions.assertEquals(ReturnStatus.STARTED_BY_USER, loadedReturn.getStatus());

    }
}
