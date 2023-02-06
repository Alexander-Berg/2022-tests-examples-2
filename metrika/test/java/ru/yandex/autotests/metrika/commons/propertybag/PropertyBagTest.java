package ru.yandex.autotests.metrika.commons.propertybag;

import org.junit.Test;

import static org.hamcrest.CoreMatchers.*;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.commons.propertybag.User.ACCESS_TOKEN;
import static ru.yandex.autotests.metrika.commons.propertybag.User.LOGIN;
import static ru.yandex.autotests.metrika.commons.propertybag.User.PASSWORD;

public class PropertyBagTest {

    private static User getUser() {
        return new User()
                .put(LOGIN, "user-name")
                .put(PASSWORD, "secret");
    }

    @Test
    public void checkProperties() {
        assertThat(getUser().getProperties(), allOf(hasItems(LOGIN, PASSWORD), not(hasItem(ACCESS_TOKEN))));
    }

    @Test
    public void checkGet() {
        assertThat(getUser().get(LOGIN), equalTo("user-name"));
    }

    @Test
    public void checkHas() {
        assertThat(getUser().has(LOGIN), equalTo(true));
    }

    @Test
    public void checkHasNot() {
        assertThat(getUser().has(ACCESS_TOKEN), equalTo(false));
    }

    @Test
    public void checkRemove() {
        User user = getUser();
        user.remove(LOGIN);
        assertThat(user.has(LOGIN), equalTo(false));
    }
}
