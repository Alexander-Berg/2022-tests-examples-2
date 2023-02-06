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

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static java.util.function.UnaryOperator.identity;
import static java.util.stream.Collectors.toMap;
import static org.hamcrest.core.IsEqual.equalTo;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_WITH_EMPTY_TOKEN;

import ru.yandex.autotests.metrika.data.common.users.Users;

/**
 * Created by sourx on 28.07.17.
 */
@Features(Requirements.Feature.JSON_SCHEMAS)
@Stories({Requirements.Story.Internal.JSON_SCHEMAS})
@Title("Cравнение json-схем старого и нового АПИ управления сегментами")
@RunWith(Parameterized.class)
public class SegmentsSchemasTest {
    private static final UserSteps user = new UserSteps().withUser(USER_WITH_EMPTY_TOKEN);

    private static final Pattern UI_PATTERN =
            Pattern.compile("^management_v1_counter_\\{counterId}_segment(?<commonSuffix>.*)$");
    private static final Pattern API_PATTERN =
            Pattern.compile("^management_v1_counter_\\{counterId}_apisegment_segment(?<commonSuffix>.*)$");

    private static Map<String, Object> schemas;

    @Parameterized.Parameter()
    public String uiPath;

    @Parameterized.Parameter(1)
    public String apiPath;

    @Parameterized.Parameters(name = "{0}: {1}")
    public static Collection<Object[]> createParameters() {
        schemas = user.onInternalSteps().getSchemas();

        Map<String, String> uiSchemas = schemas.keySet().stream()
                .filter(k -> !k.equals("_profile") && k.contains("{counterId}_segment") && !k.startsWith("internal"))
                .collect(toMap(s -> {
                    Matcher m = UI_PATTERN.matcher(s);
                    m.find();
                    return m.group("commonSuffix");
                }, identity()));
        Map<String, String> apiSchemas = schemas.keySet()
                .stream().filter(k -> !k.equals("_profile") && k.contains("{counterId}_apisegment"))
                .collect(toMap(s -> {
                    Matcher m = API_PATTERN.matcher(s);
                    m.find();
                    return m.group("commonSuffix");
                }, identity()));

        assumeThat("одинаковые схемы", uiSchemas.keySet(), equalTo(apiSchemas.keySet()));

        List<Object[]> result = new ArrayList<>();
        for (String key : uiSchemas.keySet()) {
            result.add(ArrayUtils.toArray(uiSchemas.get(key), apiSchemas.get(key)));
        }
        return result;
    }

    @Test
    public void compareSchemas() {
        assertThat("json-схемы эквивалентны", schemas.get(uiPath),
                beanEquivalent(schemas.get(apiPath)));
    }
}
