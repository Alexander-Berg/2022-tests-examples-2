package ru.yandex.autotests.audience.internal.api.tests;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import ru.yandex.audience.intapi.direct.UsersGoalsServiceInnerDmpCondition;
import ru.yandex.audience.intapi.direct.UsersGoalsServiceInnerRetargetingCondition;
import ru.yandex.audience.intapi.direct.UsersGoalsServiceInnerRetargetingConditionType;
import ru.yandex.autotests.audience.internal.api.data.GoalSubtype;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

/**
 * Created by ava1on on 02.08.17.
 */
public class IntapiTestData {
    public static final Long ACCOUNT_UID = 492616389L;
    public static final Long GUEST_UID = 495130696L;
    public static final Long ACCOUNT_WITH_CDP = 257202601L;

    public static final Long COUNTER_OWNER = 83749751L;
    public static final Long COUNTER_ID = 24226447L;
    public static final String COUNTER_NAME = "Метрика 2.0";
    public static final String COUNTER_DOMAIN = "metrika.yandex.ru";
    public static final Long METRIKA_SEGMENT_ID = 1000870109L;
    public static final String METRIKA_SEGMENT_NAME = "Был на /stat/";
    public static final Long METRIKA_GOAL_ID = 17069575L;
    public static final String METRIKA_GOAL_NAME = "Создание первого счётчика";
    public static final Long GUEST_SEGMENT_ID = 2000998208L;
    public static final Long METRIKA_COUNTER_ID = 4024226447L;
    public static final Long ECOMMERCE_COUNTER_OWNER = 228583367L;
    public static final Long ECOMMERCE_GOAL_ID = 3000101024L;
    public static final Long COUNTER_WITH_CDP = 53912887L;
    public static final String COUNTER_WITH_CDP_DOMAIN = "itsitex.ru";
    public static final Long CDP_SEGMENT_ID = 142L;
    public static final String COUNTER_WITH_CDP_NAME = "Новый";
    public static final Long CDP_SEGMENT_WITH_DATA_GOAL_ID = 269L + 2600000000L;


    public static final Long EXPERIMENT_OWNER = 202415287L;
    public static final Long EXPERIMENT_SEGMENT_ID = 2500000013L;

    public static final Long DMP_ID = 3L;
    public static final Long DMP_SEGMENT_ID = 4468L;
    public static final String DMP_TYPE = "dmp";
    public static final Long DMP_GOAL_ID = 2000998198L;

    public final static Long CRYPTA_SEGMENT_ID = 998085L;

    public final static int EXPERIMENT_ID = 101;
    public final static int NON_EXISTENT_EXPERIMENT_ID = 0;
    public final static int DELETED_EXPERIMENT_ID = 5;

    public final static int SEGMENT_A_ID = 13;
    public final static int SEGMENT_B_ID = 14;

    public final static Long UPLOADING_SEGMENT_ID = 15L;

    public final static Long COMPOSITION_SEGMENT_ID = 110234L;

    public final static Long NON_EXISTING_SEGMENT_ID = 9963081L;


    //В ImmutablePair первое значение - id сегмента + 2млрд, второе значение - охват сегмента
    public static final Map<GoalSubtype, Pair<Long, Long>> SEGMENTS = ImmutableMap.<GoalSubtype, Pair<Long, Long>>builder()
            .put(GoalSubtype.UPLOADING_EMAIL, ImmutablePair.of(2000998085L, 514434L))
            .put(GoalSubtype.UPLOADING_PHONE, ImmutablePair.of(2000998084L, 358640L))
            .put(GoalSubtype.UPLOADING_IDFA_GAID, ImmutablePair.of(2002351022L, 877710L))
            .put(GoalSubtype.UPLOADING_YUID, ImmutablePair.of(2000998086L, 1079649L))
            .put(GoalSubtype.UPLOADING_CLIENT_ID, ImmutablePair.of(2002346389L, 7667096L))
            .put(GoalSubtype.UPLOADING_MAC, ImmutablePair.of(2002347484L, 1038877L))
            .put(GoalSubtype.UPLOADING_CRM, ImmutablePair.of(2002351021L, 463716L))
            .put(GoalSubtype.METRIKA_COUNTER, ImmutablePair.of(2002351036L, 387833L))
            .put(GoalSubtype.METRIKA_SEGMENT, ImmutablePair.of(2002351037L, 178769L))
            .put(GoalSubtype.METRIKA_GOAL, ImmutablePair.of(2002351038L, 121149L))
            .put(GoalSubtype.APPMETRICA_APP, ImmutablePair.of(2002351039L, 124347L))
            .put(GoalSubtype.APPMETRICA_SEGMENT, ImmutablePair.of(2002351040L, 320331L))
            .put(GoalSubtype.GEO_CONDITION, ImmutablePair.of(2002351042L, 1783748L))
            .put(GoalSubtype.GEO_REGULAR, ImmutablePair.of(2002351041L, 331041L))
            .put(GoalSubtype.GEO_LAST, ImmutablePair.of(2002351043L, 141475L))
            .put(GoalSubtype.GEO_WORK, ImmutablePair.of(2002351045L, 831431L))
            .put(GoalSubtype.GEO_HOME, ImmutablePair.of(2002351046L, 73716L))
            .put(GoalSubtype.LOOKALIKE, ImmutablePair.of(2000594835L, 5918384L))
            .put(GoalSubtype.PIXEL, ImmutablePair.of(2000594818L, 499496L))
            .build();

    public static final UsersGoalsServiceInnerDmpCondition CONDITION = new UsersGoalsServiceInnerDmpCondition()
            .withDmpId(DMP_ID)
            .withGoalId(DMP_GOAL_ID)
            .withId(DMP_SEGMENT_ID)
            .withOwner(ACCOUNT_UID)
            .withType(DMP_TYPE);

    public static List<String> UIDS = ImmutableList.of(
            "1883838081467722609",
            "7138345721454003223",
            "1771454931495572831",
            "1903607871439039816",
            "5587713501490982556",
            "6374299681485936982",
            "5829533251476100107",
            "5190077881469998771",
            "1108595081422561214",
            "489430751493827206",
            "8136490941493573175",
            "1215191471455110408",
            "7254167921434622592",
            "6587056771489181909",
            "3981552901481746696",
            "1350830151458337397"
    );

    public static UsersGoalsServiceInnerRetargetingCondition getMetrikaCommonValues() {
        return new UsersGoalsServiceInnerRetargetingCondition()
                .withCounterId(COUNTER_ID)
                .withCounterDomain(COUNTER_DOMAIN)
                .withCounterName(COUNTER_NAME)
                .withOwner(COUNTER_OWNER);
    }

    public static UsersGoalsServiceInnerRetargetingCondition getAudienceCommonValues() {
        return new UsersGoalsServiceInnerRetargetingCondition()
                .withOwner(ACCOUNT_UID)
                .withType(UsersGoalsServiceInnerRetargetingConditionType.AUDIENCE)
                .withCounterDomain("")
                .withCounterId(0L)
                .withCounterName("");
    }

    public static UsersGoalsServiceInnerRetargetingCondition getMetrikaGoal() {
        return getMetrikaCommonValues()
                .withId(METRIKA_GOAL_ID)
                .withType(UsersGoalsServiceInnerRetargetingConditionType.GOAL)
                .withName(METRIKA_GOAL_NAME);
    }

    public static UsersGoalsServiceInnerRetargetingCondition getMetrikaSegment() {
        return getMetrikaCommonValues()
                .withId(METRIKA_SEGMENT_ID)
                .withType(UsersGoalsServiceInnerRetargetingConditionType.SEGMENT)
                .withName(METRIKA_SEGMENT_NAME);
    }

    public static UsersGoalsServiceInnerRetargetingCondition getExperimentSegment() {
        return getAudienceCommonValues()
                .withId(EXPERIMENT_SEGMENT_ID)
                .withName("Test segment A")
                .withOwner(EXPERIMENT_OWNER)
                .withPercent(50L)
                .withType(UsersGoalsServiceInnerRetargetingConditionType.AB_SEGMENT)
                .withSectionId(6L)
                .withSectionName("Test experiment")
                .withCounterIds(Arrays.asList(24226447L, 4745287L, 11010319L, 145336L, 160656L, 2237260L));
    }

    public static UsersGoalsServiceInnerRetargetingCondition getAudienceCondition(GoalSubtype subtype) {
        UsersGoalsServiceInnerRetargetingCondition result = getAudienceCommonValues()
                .withGoalSubtype(subtype.toString())
                .withId(SEGMENTS.get(subtype).getLeft())
                .withName(subtype.toString());

        if (subtype == GoalSubtype.UPLOADING_YUID)
            result.setUploadingSourceId("3");
        return result;
    }

    public static UsersGoalsServiceInnerRetargetingCondition getFewDataAudienceCondition() {
        return getAudienceCommonValues()
                .withGoalSubtype(GoalSubtype.PIXEL.toString())
                .withId(2000594877L)
                .withName("мало данных");
    }

    public static UsersGoalsServiceInnerRetargetingCondition getGuestAudienceSegment() {
        return getAudienceCommonValues()
                .withGoalSubtype(GoalSubtype.GEO_REGULAR.toString())
                .withId(GUEST_SEGMENT_ID)
                .withName("regular")
                .withOwner(GUEST_UID);
    }

    public static UsersGoalsServiceInnerRetargetingCondition getEcommerceGoal() {
        return new UsersGoalsServiceInnerRetargetingCondition()
                .withOwner(ECOMMERCE_COUNTER_OWNER)
                .withId(ECOMMERCE_GOAL_ID)
                .withType(UsersGoalsServiceInnerRetargetingConditionType.ECOMMERCE)
                .withCounterId(ECOMMERCE_GOAL_ID - 3000000000L)
                .withCounterDomain("sendflowers.ru");
    }

    public static UsersGoalsServiceInnerRetargetingCondition getCdpSegment() {
        return new UsersGoalsServiceInnerRetargetingCondition()
                .withOwner(ACCOUNT_WITH_CDP)
                .withId(CDP_SEGMENT_ID + 2600000000L)
                .withType(UsersGoalsServiceInnerRetargetingConditionType.CDP_SEGMENT)
                .withCounterId(COUNTER_WITH_CDP)
                .withCounterDomain(COUNTER_WITH_CDP_DOMAIN)
                .withCounterName(COUNTER_WITH_CDP_NAME);
    }
}
