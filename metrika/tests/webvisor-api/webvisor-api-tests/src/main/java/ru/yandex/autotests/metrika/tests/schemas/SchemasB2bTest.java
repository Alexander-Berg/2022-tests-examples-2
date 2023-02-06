package ru.yandex.autotests.metrika.tests.schemas;

import org.apache.commons.lang3.ArrayUtils;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import static java.util.stream.Collectors.toList;
import static java.util.stream.Collectors.toSet;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraints.ignore;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_WITH_EMPTY_TOKEN;
/**
 * Created by konkov on 07.07.2016.
 */
@Features(Requirements.Feature.JSON_SCHEMAS)
@Stories({Requirements.Story.Internal.JSON_SCHEMAS})
@Title("B2B - Метаданные: сравнение json-схем")
@RunWith(Parameterized.class)
public class SchemasB2bTest {
    private static final UserSteps userOnTest = new UserSteps().withUser(USER_WITH_EMPTY_TOKEN);
    private static final UserSteps userOnRef = new UserSteps().withUser(USER_WITH_EMPTY_TOKEN).useReference();

    private static Map<String, Object> schemasRef;
    private static Map<String, Object> schemasTest;

    @Parameterized.Parameter()
    public String path;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        schemasRef = userOnRef.onInternalSteps().getSchemas();
        schemasTest = userOnTest.onInternalSteps().getSchemas();

        Set<String> paths = new HashSet<>();
        paths.addAll(schemasRef.keySet().stream().filter(k -> !k.equals("_profile")).collect(toSet()));
        paths.addAll(schemasTest.keySet().stream().filter(k -> !k.equals("_profile")).collect(toSet()));

        return paths.stream()
                .sorted()
                .map(ArrayUtils::toArray)
                .collect(toList());
    }

    @Test
    public void compareSchemas() {
        /*
        1. get ref schema
        2. get test schema
        3. beandiffer
        4. ...
        5. PROFIT
         */

        assertThat("json-схемы эквивалентны", schemasTest.get(path),
                beanEquivalent(schemasRef.get(path)).fields(ignore("properties/query/additionalProperties", "additionalProperties")));
    }
}
