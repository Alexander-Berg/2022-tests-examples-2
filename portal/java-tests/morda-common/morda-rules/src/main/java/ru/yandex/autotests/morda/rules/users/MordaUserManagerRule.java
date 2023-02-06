package ru.yandex.autotests.morda.rules.users;

import ru.yandex.qatools.usermanager.UserManagerRule;
import ru.yandex.qatools.usermanager.beans.UserData;

import java.util.List;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/05/16
 */
public class MordaUserManagerRule extends UserManagerRule {

    public UserData getMordaUser(MordaUserTag... tags) {
        return getMordaUser(asList(tags));
    }

    public UserData getMordaUser(List<MordaUserTag> tags) {
        List<String> stringTags = tags.stream().map(MordaUserTag::getValue).collect(Collectors.toList());
        stringTags.add(MordaUserTag.MORDA_TAG);
        return getUser(stringTags);
    }
}
