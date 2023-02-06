package ru.yandex.metrika.mobmet.push.api.model;

import java.io.IOException;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Test;

import ru.yandex.metrika.mobmet.push.api.model.send.PushApiBatchRequestAdapterWrapper;
import ru.yandex.metrika.util.io.IOUtils;
import ru.yandex.metrika.util.json.ObjectMappersFactory;

import static org.junit.Assert.assertEquals;

public class PushApiBatchRequestAdapterWrapperTest {

    private static final ObjectMapper defaultMapper = ObjectMappersFactory.getDefaultMapper();
    private static final String EXPECTED =
            IOUtils.resourceAsString(PushApiBatchRequestAdapterWrapperTest.class, "push_batch_request.json")
                    .replaceAll("\\s", "");

    @Test
    public void testToFromJsonMapping() throws IOException {
        PushApiBatchRequestAdapterWrapper request =
                defaultMapper.readValue(EXPECTED, PushApiBatchRequestAdapterWrapper.class);
        String actual = defaultMapper.writeValueAsString(request);

        assertEquals(EXPECTED, actual);
    }
}
