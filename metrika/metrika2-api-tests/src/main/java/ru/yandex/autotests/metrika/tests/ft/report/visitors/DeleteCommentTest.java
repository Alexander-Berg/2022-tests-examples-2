package ru.yandex.autotests.metrika.tests.ft.report.visitors;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.irt.testutils.RandomUtils;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1UserInfoGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.parameters.visitors.VisitorCommentParameters;
import ru.yandex.autotests.metrika.data.parameters.visitors.VisitorInfoParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.core.IsEqual.equalTo;
import static ru.yandex.autotests.metrika.data.common.users.Users.METRIKA_TEST_COUNTERS;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.VISITORS)
@Stories({Requirements.Story.Visitors.COMMENTS})
@Title("Удаления комментария к посетителю")
public class DeleteCommentTest {

    private static final String COMMENT_DIMENSION = "ym:u:userComment";

    private static final String USER_ID_HASH = "1905833125";
    private static final String USER_ID_HASH_64 = "5126477719299274544";
    private static final String FIRST_VISIT_DATE = "2018-07-03";

    private static final Long counterId = Counters.MELDA_RU.getId();
    private static final UserSteps owner = new UserSteps().withUser(METRIKA_TEST_COUNTERS);

    @Before
    public void setup() {
        String comment = RandomUtils.getString(10);
        owner.onVisitorsSteps().addCommentAndExpectSuccess(new VisitorCommentParameters()
                .withComment(comment)
                .withId(counterId)
                .withUserIdHash(USER_ID_HASH)
                .withUserIdHash64(USER_ID_HASH_64)
                .withFirstVisitDate(FIRST_VISIT_DATE)
        );
    }

    @Test
    public void deleteCommentTest() {
        VisitorInfoParameters params = new VisitorInfoParameters()
                .withId(counterId)
                .withUserIdHash(USER_ID_HASH)
                .withUserIdHash64(USER_ID_HASH_64)
                .withFirstVisitDate(FIRST_VISIT_DATE);

        owner.onVisitorsSteps().deleteCommentAndExpectSuccess(params);

        StatV1UserInfoGETSchema info = owner.onVisitorsSteps().getVisitorInfoAndExpectSuccess(params);
        int commentDimensionIndex = info.getQuery().getDimensions().indexOf(COMMENT_DIMENSION);
        String commentData = (String) info.getData().get(0).getDimensions().get(commentDimensionIndex).get("name");
        assertThat("Комментарий удален", commentData, equalTo(null));
    }


}
