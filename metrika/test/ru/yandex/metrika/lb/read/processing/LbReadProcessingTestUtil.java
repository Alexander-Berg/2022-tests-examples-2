package ru.yandex.metrika.lb.read.processing;

import java.nio.charset.StandardCharsets;

public class LbReadProcessingTestUtil {

    public static <T> LogbrokerRichMessage<T> lbMessage(T t) {
        return new LogbrokerRichMessage<>(
                new LogbrokerMessageExtra("/some/topic", 1, "source_id".getBytes(StandardCharsets.UTF_8), 1, 0, 0), t
        );
    }
}
