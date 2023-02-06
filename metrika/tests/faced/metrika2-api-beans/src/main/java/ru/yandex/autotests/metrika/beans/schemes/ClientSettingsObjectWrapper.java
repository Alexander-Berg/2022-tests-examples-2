package ru.yandex.autotests.metrika.beans.schemes;

import com.rits.cloning.Cloner;
import ru.yandex.metrika.api.management.client.ClientSettings;

/**
 * Created by omatikaya on 17.03.17.
 */
public class ClientSettingsObjectWrapper {
    private final ClientSettings value;

    public ClientSettingsObjectWrapper(ClientSettings value) {
        this.value = value;
    }

    public ClientSettings get() {
        return value;
    }

    private final static Cloner CLONER = new Cloner();

    @Override
    public String toString() {
        return value == null ? "null"
                : "[subscription=" + value.getSubscriptionEmails() + ",unchecked="
                + value.getSubscriptionEmailsUnchecked() + "]" ;
    }

    public ClientSettings getClone() {
        return CLONER.deepClone(value);
    }
}
