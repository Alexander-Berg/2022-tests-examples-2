package ru.yandex.metrika.mobmet.intapi.takeout;

import java.io.IOException;
import java.io.UncheckedIOException;

import ru.yandex.metrika.util.json.ObjectMappersFactory;

import static org.assertj.core.api.Assumptions.assumeThat;

public class TakeoutTestUtils {

    private TakeoutTestUtils() {
    }

    public static TakeoutOkResponse readOkTakeoutResponse(TakeoutResponse response) {
        assumeThat(response.getTakeoutStatus()).isEqualTo("ok");
        String dataJson = response.getData().get("data.json");
        try {
            return ObjectMappersFactory.getDefaultMapper().readValue(dataJson, TakeoutOkResponse.class);
        } catch (IOException ex) {
            throw new UncheckedIOException(ex);
        }
    }
}
