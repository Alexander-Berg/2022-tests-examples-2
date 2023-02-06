package ru.yandex.autotests.metrika.appmetrica.wrappers;

import com.rits.cloning.Cloner;
import ru.yandex.metrika.mobmet.management.ApplicationCreationInfo;

/**
 * Created by konkov on 15.09.2016.
 */
public class ApplicationCreationInfoWrapper {
    private final static Cloner CLONER = new Cloner();

    private final ApplicationCreationInfo value;

    public ApplicationCreationInfoWrapper(ApplicationCreationInfo value) {
        this.value = value;
    }

    public ApplicationCreationInfo get() {
        return value;
    }

    public ApplicationCreationInfo getClone() {
        return CLONER.deepClone(value);
    }

    @Override
    public String toString() {
        return value == null ? "null"
                : value.getName();
    }

}
