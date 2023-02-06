package ru.yandex.metrika.mobile.push.api.tests;

import org.hamcrest.Matcher;

import ru.yandex.metrika.mobmet.push.api.model.PushGroupAdapter;

import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanDiffer;
import static ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraints.ignore;

public class Matchers {

    public static Matcher<PushGroupAdapter> matchGroup(PushGroupAdapter expectedGroup) {
        return beanDiffer(expectedGroup).fields(ignore("id", "subject/id"));
    }

}
