package ru.yandex.metrika.mobile.push.api.tests;

import io.qameta.allure.Story;
import org.junit.Test;

import ru.yandex.qatools.allure.annotations.Title;

@Story("Ping")
public class PushApiPingTest extends PushApiBaseTest {

    @Test
    @Title("Ручка ping")
    public void pushApiPingTest() throws Exception {
        steps.assertGetSuccess(mockMvc, "/ping");
    }

}
