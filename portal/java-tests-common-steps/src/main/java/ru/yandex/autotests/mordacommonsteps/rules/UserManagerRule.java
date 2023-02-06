package ru.yandex.autotests.mordacommonsteps.rules;

import ru.yandex.autotests.mordacommonsteps.utils.Mode;
import ru.yandex.autotests.utils.morda.users.BaseUser;
import ru.yandex.autotests.utils.morda.users.PlainUser;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.autotests.utils.morda.users.UserType;
import ru.yandex.autotests.utils.morda.users.WidgetUser;
import ru.yandex.qatools.usermanager.beans.UserData;

import java.util.ArrayList;
import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/05/16
 */
public class UserManagerRule extends ru.yandex.qatools.usermanager.UserManagerRule {

    public User getUser(BaseUser baseUser) {
        List<String> tags = new ArrayList<>();
        tags.add("morda");
        tags.add(baseUser.getType().getName().toLowerCase());
        if (baseUser instanceof WidgetUser) {
            tags.add("widget");
        } else {
            tags.add("default");
        }
        System.out.println(tags);
        UserData data = getUser(tags);
        return new User(null, data.getLogin(), data.getPassword());
    }

    public User getUser(UserType type) {
        return getUser(type, Mode.PLAIN);
    }

    public User getUser(UserType type, Mode mode) {

        List<String> tags = new ArrayList<>();
        tags.add("morda");
        tags.add(type.getName().toLowerCase());
        if (mode == Mode.WIDGET) {
            tags.add("widget");
        } else {
            tags.add("default");
        }
        System.out.println(tags);
        UserData data = getUser(tags);
        return new User(null, data.getLogin(), data.getPassword());
    }

    public static void main(String[] args) {
        UserManagerRule userManagerRule = new UserManagerRule();
        System.out.println(userManagerRule.getUser(PlainUser.plainUser(UserType.DEFAULT)).getLogin());
    }
}
