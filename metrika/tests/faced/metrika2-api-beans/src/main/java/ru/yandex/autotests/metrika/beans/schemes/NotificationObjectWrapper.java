package ru.yandex.autotests.metrika.beans.schemes;

import com.rits.cloning.Cloner;
import ru.yandex.metrika.api.management.client.notification.Notification;

/**
 * Created by sourx on 26.07.16.
 */
public class NotificationObjectWrapper {
    private final Notification value;

    public NotificationObjectWrapper(Notification value) {
        this.value = value;
    }

    public Notification get() {
        return value;
    }

    private final static Cloner CLONER = new Cloner();

    @Override
    public String toString() {
        return value == null ? "null"
                : value.getContent().getTitle().toString();
    }

    public Notification getClone() {
        return CLONER.deepClone(value);
    }
}
