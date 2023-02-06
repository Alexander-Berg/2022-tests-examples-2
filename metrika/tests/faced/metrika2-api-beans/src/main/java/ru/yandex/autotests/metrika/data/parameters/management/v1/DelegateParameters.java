package ru.yandex.autotests.metrika.data.parameters.management.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.users.User;

import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;

/**
 * Created by konkov on 29.12.2014.
 *
 * Параметр ulogin для использования представительства в API
 */
public class DelegateParameters extends AbstractFormParameters {

    @FormParameter("ulogin")
    private String userLogin;

    public String getUserLogin() {
        return userLogin;
    }

    public void setUserLogin(String userLogin) {
        this.userLogin = userLogin;
    }

    public DelegateParameters withUserLogin(String userLogin) {
        this.userLogin = userLogin;
        return this;
    }

    public static DelegateParameters ulogin(String userLogin) {
        return new DelegateParameters().withUserLogin(userLogin);
    }

    public static DelegateParameters ulogin(User user) {
        return ulogin(user.get(LOGIN));
    }

    public static DelegateParameters ulogin(Counter counter) {
        return ulogin(counter.get(Counter.U_LOGIN));
    }
}
