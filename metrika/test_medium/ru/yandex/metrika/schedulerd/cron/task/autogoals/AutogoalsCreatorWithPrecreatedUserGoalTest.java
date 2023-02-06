package ru.yandex.metrika.schedulerd.cron.task.autogoals;

import java.util.ArrayList;
import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.function.BiConsumer;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.test.context.ContextConfiguration;

import ru.yandex.metrika.api.management.client.external.goals.ActionGoal;
import ru.yandex.metrika.api.management.client.external.goals.ContactDataGoal;
import ru.yandex.metrika.api.management.client.external.goals.EmailGoal;
import ru.yandex.metrika.api.management.client.external.goals.FileGoal;
import ru.yandex.metrika.api.management.client.external.goals.FormGoal;
import ru.yandex.metrika.api.management.client.external.goals.GoalCondition;
import ru.yandex.metrika.api.management.client.external.goals.GoalConditionType;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.goals.GoalSource;
import ru.yandex.metrika.api.management.client.external.goals.LoginWithYandexCIDGoal;
import ru.yandex.metrika.api.management.client.external.goals.MessengerGoal;
import ru.yandex.metrika.api.management.client.external.goals.PaymentSystemGoal;
import ru.yandex.metrika.api.management.client.external.goals.PhoneGoal;
import ru.yandex.metrika.api.management.client.external.goals.SiteSearchGoal;
import ru.yandex.metrika.api.management.client.external.goals.SocialNetworkGoal;
import ru.yandex.metrika.autogoals.AutoGoals;

/**
 * автоцели создаются при наличии удалённой пользовательской цели такого же типа,
 * и не создаются, если есть активная пользовательская цель такого же типа
 *
 * для партнёрских (action) целей, всё то же самое, но на уровне url'а condition'а, а не на уровне типа цели
 */
@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractAutogoalsCreatorTest.AutogoalsConfig.class})
public class AutogoalsCreatorWithPrecreatedUserGoalTest extends AbstractAutogoalsCreatorTest {

    @Parameterized.Parameter
    public AutogoalCandidateInfoBrief input;

    @Parameterized.Parameter(1)
    public String testName;

    @Parameterized.Parameter(2)
    public boolean deletePrecreatedGoal;

    @Parameterized.Parameter(3)
    public GoalE userGoalToCreateBefore;

    static BiConsumer<Boolean, List<Object[]>> forCommonAutoGoals = (deletePrecreatedGoal, acc) -> {
        for (int i = 0; i < limit; i++) {
            if (AutogoalsCreatorWithPrecreatedUserGoalTest.getIgnoredTypes().contains(i)) {
                continue;
            }
            acc.add(new Object[]{
                    new AutogoalCandidateInfoBrief(
                            getCounterIdWithEnabledAutogoals(),
                            new int[]{i},
                            new String[]{}
                    ),
                    "AutogoalsCreator test with precreated" +
                            (deletePrecreatedGoal ? " and deleted" : "") +
                            " user goal, type = " + AutoGoals.Type.forNumber(i),
                    deletePrecreatedGoal,
                    getUserGoalByAutogoalsType(AutoGoals.Type.forNumber(i))
            });
        }
    };

    static BiConsumer<Boolean, List<Object[]>> forPartnersGoals = (deletePrecreatedGoal, acc) -> {
        for (var partnersGoalAction : allPartnerAutogoalsToTest) {
            acc.add(new Object[]{
                    new AutogoalCandidateInfoBrief(
                            getCounterIdWithEnabledAutogoals(),
                            new int[]{AutoGoals.Type.PARTNER_VALUE},
                            new String[]{partnersGoalAction}
                    ), "AutogoalsCreator test with precreated" +
                    (deletePrecreatedGoal ? " and deleted" : "") +
                    " partners user goal, action type = " + partnersGoalAction,
                    deletePrecreatedGoal,
                    getPartnerUserGoalByActionName(partnersGoalAction)
            });
        }
    };


    @Parameterized.Parameters(name = "{1}")
    public static List<Object[]> getParameters() {
        var result = new ArrayList<Object[]>();

        Set.of(true, false).forEach(dPG -> {
            forCommonAutoGoals.accept(dPG, result);
            forPartnersGoals.accept(dPG, result);
        });
        return result;
    }

    @Before
    public void pre() {
        cleanAllGoals(input.getCounterId());
        goalsService.create(input.getCounterId(), userGoalToCreateBefore);
        if (deletePrecreatedGoal) {
            markAllGoalsAsDeleted(input.getCounterId());
        }
    }

    @Test
    public void test() {
        autogoalsCreator.checkAndCreateOrUpdate(List.of(input));

        // проверяем наличие одной активной цели нужного типа,
        // в зависимости от deletePrecreatedGoal это должна быть либо предсозданная пользовательская, либо автоцель
        // для партнёрских целей, всё то же самое, но на уровне url'а condition'а - то есть action'а цели, а не на уровне типа цели
        var goals = goalsService.findByCounterId(input.getCounterId(), false);
        Assert.assertEquals(1, goals.size());
        var goal = goals.get(0);
        Assert.assertEquals(input.getCounterId(), goal.getCounterId());
        if (deletePrecreatedGoal) {
            Assert.assertEquals(GoalSource.auto, goal.getGoalSource());
        } else {
            Assert.assertEquals(GoalSource.user, goal.getGoalSource());
        }
        Assert.assertEquals(autogoalsCreator.getGoalTypeFromCH(input.getAutogoalsTypesToCreate()[0]), goal.getType());
    }

    protected static Set<Integer> getIgnoredTypes() {
        var result = new HashSet<>(AbstractAutogoalsCreatorTest.getIgnoredTypes());
        result.add(7);  //can't create e_cart user goal so also skip for this test
        return result;
    }

    static GoalE getUserGoalByAutogoalsType(AutoGoals.Type goalType) {
        GoalE result = null;
        var condition = new GoalCondition();
        switch (goalType) {
            case PHONE:
                result = new PhoneGoal();
                ((PhoneGoal) result).setConditions(List.of());
                break;
            case FORM:
                result = new FormGoal();
                ((FormGoal) result).setConditions(List.of());
                break;
            case EMAIL:
                result = new EmailGoal();
                ((EmailGoal) result).setConditions(List.of());
                break;
            case MESSENGER:
                result = new MessengerGoal();
                condition.setOperator(GoalConditionType.messenger);
                condition.setValue("all_messengers");
                ((MessengerGoal) result).setConditions(List.of(condition));
                break;
            case FILE:
                result = new FileGoal();
                condition.setOperator(GoalConditionType.file);
                condition.setValue("abrakadabra");
                ((FileGoal) result).setConditions(List.of(condition));
                break;
            case SEARCH:
                result = new SiteSearchGoal();
                condition.setOperator(GoalConditionType.search);
                condition.setValue("q");
                ((SiteSearchGoal) result).setConditions(List.of(condition));
                break;
            case PURCHASE:
            case CART:      // не бывает пользовательской
            case PARTNER:   // создается в getPartnerUserGoalByActionName
                return null;
            case PAYMENT_SYSTEM:
                result = new PaymentSystemGoal();
                break;
            case SOCIAL:
                result = new SocialNetworkGoal();
                condition.setOperator(GoalConditionType.social);
                condition.setValue("twitter");
                ((SocialNetworkGoal) result).setConditions(List.of(condition));
                break;
            case CONTACT_DATA:
                result = new ContactDataGoal();
                break;
            case LOGIN_WITH_YANDEXCID:
                result = new LoginWithYandexCIDGoal();
                break;
            case UNRECOGNIZED:
                return null;
        }
        result.setGoalSource(GoalSource.user);
        result.setCreateTime(new Date());
        result.setName("Some user goal");
        return result;
    }

    static ActionGoal getPartnerUserGoalByActionName(String partnersGoalAction) {
        var partnerGoal = new ActionGoal();
        partnerGoal.setCreateTime(new Date());
        partnerGoal.setGoalSource(GoalSource.user);
        partnerGoal.setName("User partners goal");

        var condition = new GoalCondition();
        condition.setOperator(partnersGoalsRegexpActionsMap.containsKey(partnersGoalAction) ?
                GoalConditionType.regexp : GoalConditionType.exact);
        condition.setValue(partnersGoalsRegexpActionsMap.getOrDefault(partnersGoalAction, partnersGoalAction));
        partnerGoal.setConditions(List.of(condition));
        return partnerGoal;
    }
}
