package ru.yandex.metrika.mobmet.push.common.campaigns.model;

import java.util.Collections;
import java.util.List;

import ru.yandex.metrika.mobmet.push.common.campaigns.validation.ValidationError;

/**
 * Отправка на тестовое устройство.
 * Либо все окей, либо у нас не прошла валидация конкретного сообщения.
 * <p>
 * Created by graev on 14/09/16.
 */
public final class TestPushStatus {
    private final boolean ok;
    private final List<ValidationError> errors;

    public static TestPushStatus ok() {
        return new TestPushStatus(true, Collections.emptyList());
    }

    public static TestPushStatus notOk(List<ValidationError> errors) {
        return new TestPushStatus(false, errors);
    }

    private TestPushStatus(boolean ok, List<ValidationError> errors) {
        this.ok = ok;
        this.errors = errors;
    }

    public boolean isOk() {
        return ok;
    }

    public List<ValidationError> getErrors() {
        return errors;
    }
}
