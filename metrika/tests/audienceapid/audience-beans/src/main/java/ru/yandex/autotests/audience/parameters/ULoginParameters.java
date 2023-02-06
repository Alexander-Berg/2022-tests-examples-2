package ru.yandex.autotests.audience.parameters;

import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

/**
 * Created by ava1on on 14.06.17.
 */
public class ULoginParameters extends AbstractFormParameters{
    @FormParameter("ulogin")
    private String ulogin;

    public String getUlogin() {
        return ulogin;
    }

    public void setUlogin(String ulogin) {
        this.ulogin = ulogin;
    }

    public ULoginParameters withUlogin(final String ulogin) {
        this.ulogin = ulogin;
        return this;
    }

    public static ULoginParameters ulogin(String ulogin) {
        return new ULoginParameters().withUlogin(ulogin);
    }

    public static ULoginParameters ulogin(User user) {
        return ulogin(user.toString());
    }
}
