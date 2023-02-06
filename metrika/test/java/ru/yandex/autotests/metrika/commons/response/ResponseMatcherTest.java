package ru.yandex.autotests.metrika.commons.response;

import org.hamcrest.Description;
import org.hamcrest.StringDescription;
import org.junit.Test;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.both;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectErrorCode;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

/**
 * Created by konkov on 06.03.2015.
 */
public class ResponseMatcherTest {

    private final static GETSchema SUCCESS_RESPONSE = new GETSchema()
            .withCode(null)
            .withMessage(null);

    private final static GETSchema ERROR_RESPONSE = new GETSchema()
            .withCode(503L)
            .withMessage("Internal server error");

    @Test
    public void checkExpectSuccess() {
        assertThat(SUCCESS_RESPONSE, expectSuccess());
    }

    @Test
    public void checkExpectErrorCode() {
        assertThat(ERROR_RESPONSE, expectErrorCode(503L));
    }

    @Test
    public void checkExpectError() {
        assertThat(ERROR_RESPONSE, expectError(ERROR_RESPONSE.getCode(), ERROR_RESPONSE.getMessage()));
    }

    @Test
    public void checkMessage() {
        Description description = new StringDescription();

        expectSuccess().describeMismatch(ERROR_RESPONSE, description);

        assertThat(description.toString(),
                both(containsString(ERROR_RESPONSE.getCode().toString()))
                        .and(containsString(ERROR_RESPONSE.getMessage())));
    }
}
