package ru.yandex.autotests.metrika.core;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import ru.yandex.autotests.metrika.core.jodatime.DateTimeConverter;
import ru.yandex.autotests.metrika.core.jodatime.LocalDateConverter;
import ru.yandex.autotests.metrika.core.jodatime.LocalDateTimeConverter;
import ru.yandex.autotests.metrika.core.jodatime.LocalTimeConverter;
import ru.yandex.autotests.metrika.data.b2b.B2bSample;
import ru.yandex.autotests.metrika.factories.LowercaseEnumTypeAdapterFactory;
import ru.yandex.autotests.metrika.serializers.B2bSampleDeserializer;
import ru.yandex.autotests.metrika.serializers.GoalDeserializer;
import ru.yandex.autotests.metrika.serializers.Jackson2FieldNamingStrategy;
import ru.yandex.metrika.api.management.client.external.goals.*;
import ru.yandex.metrika.api.management.client.external.goals.call.ConditionalCallGoal;

import static ru.yandex.autotests.metrika.core.jodatime.DateTimeConverter.DATE_TIME_TYPE;
import static ru.yandex.autotests.metrika.core.jodatime.LocalDateConverter.LOCAL_DATE_TYPE;
import static ru.yandex.autotests.metrika.core.jodatime.LocalDateTimeConverter.LOCAL_DATE_TIME_TYPE;
import static ru.yandex.autotests.metrika.core.jodatime.LocalTimeConverter.LOCAL_TIME_TYPE;
import static ru.yandex.autotests.metrika.utils.Utils.JSON_DATE_FORMAT;

/**
 * Created by konkov on 20.03.2015.
 */
public class MetrikaJson {

    public static final Gson GSON_RESPONSE = new GsonBuilder()
            .registerTypeAdapter(GoalE.class, new GoalDeserializer()
                            .registerGoalType(UrlGoal.class, GoalType.URL)
                            .registerGoalType(ActionGoal.class, GoalType.ACTION)
                            .registerGoalType(DepthGoal.class, GoalType.NUMBER)
                            .registerGoalType(CompositeGoal.class, GoalType.STEP)
                            .registerGoalType(CallGoal.class, GoalType.CALL)
                            .registerGoalType(PhoneGoal.class, GoalType.PHONE)
                            .registerGoalType(EmailGoal.class, GoalType.EMAIL)
                            .registerGoalType(FormGoal.class, GoalType.FORM)
                            .registerGoalType(PaymentSystemGoal.class, GoalType.PAYMENT_SYSTEM)
                            .registerGoalType(MessengerGoal.class, GoalType.MESSENGER)
                            .registerGoalType(FileGoal.class, GoalType.FILE)
                            .registerGoalType(SiteSearchGoal.class, GoalType.SEARCH)
                            .registerGoalType(ButtonGoal.class, GoalType.BUTTON)
                            .registerGoalType(ConditionalCallGoal.class, GoalType.CONDITIONAL_CALL)
                            .registerGoalType(SocialNetworkGoal.class, GoalType.SOCIAL)
            )
            .enableComplexMapKeySerialization()
            .setDateFormat(JSON_DATE_FORMAT)
            .setFieldNamingStrategy(Jackson2FieldNamingStrategy.STRATEGY)
            .setPrettyPrinting()
            .registerTypeAdapterFactory(new LowercaseEnumTypeAdapterFactory())
            .registerTypeAdapter(DATE_TIME_TYPE, new DateTimeConverter())
            .registerTypeAdapter(LOCAL_DATE_TIME_TYPE, new LocalDateTimeConverter())
            .registerTypeAdapter(LOCAL_DATE_TYPE, new LocalDateConverter())
            .registerTypeAdapter(LOCAL_TIME_TYPE, new LocalTimeConverter())
            .serializeNulls()
            .create();

    public static final Gson GSON_REQUEST = new GsonBuilder()
            .enableComplexMapKeySerialization()
            .setDateFormat(JSON_DATE_FORMAT)
            .setFieldNamingStrategy(Jackson2FieldNamingStrategy.STRATEGY)
            .setPrettyPrinting()
            .registerTypeAdapterFactory(new LowercaseEnumTypeAdapterFactory())
            .registerTypeAdapter(DATE_TIME_TYPE, new DateTimeConverter())
            .registerTypeAdapter(LOCAL_DATE_TIME_TYPE, new LocalDateTimeConverter())
            .registerTypeAdapter(LOCAL_DATE_TYPE, new LocalDateConverter())
            .registerTypeAdapter(LOCAL_TIME_TYPE, new LocalTimeConverter())
            .create();

    public static final Gson GSON_B2B_SAMPLE = new GsonBuilder()
            .registerTypeAdapter(B2bSample.class, new B2bSampleDeserializer())
            .create();
}
