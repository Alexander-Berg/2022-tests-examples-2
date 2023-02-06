package ru.yandex.autotests.metrika.retry;

import com.google.common.collect.ImmutableList;
import org.apache.commons.io.IOUtils;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.beans.schemes.ProfileOnlySchema;
import ru.yandex.autotests.metrika.core.MetrikaJson;
import ru.yandex.autotests.metrika.core.Retry;

import java.io.IOException;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assert.assertThat;

/**
 * Created by konkov on 27.06.2017.
 */
@RunWith(Parameterized.class)
public class RetryTest {

    @Parameterized.Parameter(0)
    public String resourceName;

    @Parameterized.Parameter(1)
    public Boolean shouldRetry;

    @Parameterized.Parameters(name = "{0} : {1}")
    public static Iterable<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(toArray("QueryIsExecutingTooSlow.json", true))
                .add(toArray("InvalidOauthToken.json", false))
                .add(toArray("FailedToRespondAtNull.json", true))
                .add(toArray("FailedConnectTimedOutAtNull.json", true))
                .add(toArray("QueryLogHaveBeenAlreadyShutdown.json", true))
                .build();
    }

    @Test
    public void test() throws IOException {
        String s = IOUtils.toString(this.getClass().getResourceAsStream(resourceName));

        ProfileOnlySchema profileOnlySchema = MetrikaJson.GSON_RESPONSE.fromJson(s, ProfileOnlySchema.class);

        assertThat(Retry.isRetryable(profileOnlySchema), equalTo(shouldRetry));
    }
}
