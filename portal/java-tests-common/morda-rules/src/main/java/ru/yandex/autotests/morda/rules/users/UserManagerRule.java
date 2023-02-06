package ru.yandex.autotests.morda.rules.users;

import org.junit.rules.TestWatcher;
import org.junit.runner.Description;
import ru.yandex.autotests.mordacommonsteps.utils.Mode;
import ru.yandex.autotests.utils.morda.users.BaseUser;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.autotests.utils.morda.users.UserManager;
import ru.yandex.autotests.utils.morda.users.UserType;

import java.util.ArrayList;
import java.util.List;

import static ru.yandex.autotests.utils.morda.users.PlainUser.plainUser;
import static ru.yandex.autotests.utils.morda.users.WidgetUser.widgetUser;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 31.01.14
 */
public class UserManagerRule extends TestWatcher {
    private UserManager userManager;
    private List<User> users;

    public UserManagerRule() {
        this.userManager = new UserManager();
        this.users = new ArrayList<>();
    }

    public User getUser(BaseUser baseUser) {
        User user = userManager.getUser(baseUser);
        users.add(user);
        return user;
    }

    public User getUser(UserType type) {
        return getUser(type, Mode.PLAIN);
    }

    public User getUser(UserType type, Mode mode) {
        BaseUser baseUser;

        if (mode.equals(Mode.WIDGET)) {
            baseUser = widgetUser(type);
        } else {
            baseUser = plainUser(type);
        }

        User user = userManager.getUser(baseUser);
        users.add(user);
        return user;
    }

    @Override
    protected void finished(Description description) {
       if (!users.isEmpty()) {
            userManager.releaseUsers(users);
       }
    }
}
