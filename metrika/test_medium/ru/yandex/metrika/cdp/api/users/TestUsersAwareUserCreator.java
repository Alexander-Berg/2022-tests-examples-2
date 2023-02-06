package ru.yandex.metrika.cdp.api.users;

import java.util.Optional;

import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.rbac.UserCreator;

public class TestUsersAwareUserCreator extends UserCreator {

    @Override
    protected String getLogin(long uid) {
        return Optional.ofNullable(TestUsers.usersByUid.get(uid))
                .map(MetrikaUserDetails::getUsername)
                .orElseGet(() -> super.getLogin(uid));
    }
}
