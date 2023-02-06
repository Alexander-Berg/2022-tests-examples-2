package ru.yandex.metrika.mobmet.push.common.campaigns.adapters;

import java.util.List;
import java.util.stream.Collectors;

import ru.yandex.metrika.mobmet.push.common.campaigns.model.TestPushStatus;
import ru.yandex.metrika.mobmet.push.common.campaigns.validation.ValidationError;
import ru.yandex.metrika.util.collections.F;

/**
 * Конвертируем ошибки в удобное представление для фронтенда
 * <p>
 * Created by graev on 06/10/16.
 */
public final class TestPushStatusAdapter {
    private final boolean ok;

    private final List<ValidationErrorAdapter> errors;

    public TestPushStatusAdapter(TestPushStatus subject) {
        ok = subject.isOk();
        errors = subject.getErrors().stream()
                .flatMap(e -> createErrorAdapters(e).stream())
                .collect(Collectors.toList());
    }

    private static List<ValidationErrorAdapter> createErrorAdapters(ValidationError error) {
        return F.map(error.getLocations(), location -> new ValidationErrorAdapter(error, location));
    }

    public boolean isOk() {
        return ok;
    }

    public List<ValidationErrorAdapter> getErrors() {
        return errors;
    }
}
