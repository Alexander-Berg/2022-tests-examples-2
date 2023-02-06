package ru.yandex.metrika.schedulerd.cron.task.autogoals;

import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import javax.annotation.ParametersAreNonnullByDefault;
import javax.validation.Validator;

import org.junit.ClassRule;
import org.junit.Rule;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.ImportResource;
import org.springframework.test.context.junit4.rules.SpringClassRule;
import org.springframework.test.context.junit4.rules.SpringMethodRule;
import org.springframework.validation.beanvalidation.LocalValidatorFactoryBean;

import ru.yandex.metrika.api.management.client.CounterLimitsService;
import ru.yandex.metrika.api.management.client.DefaultCounterLimitsService;
import ru.yandex.metrika.api.management.client.FormGoalsService;
import ru.yandex.metrika.api.management.client.GoalIdGenerationService;
import ru.yandex.metrika.api.management.client.GoalsService;
import ru.yandex.metrika.api.management.client.MessengerService;
import ru.yandex.metrika.api.management.client.SocialNetworkService;
import ru.yandex.metrika.api.management.client.autogoals.PartnersGoalsDao;
import ru.yandex.metrika.api.management.client.external.goals.GoalConditionValidator;
import ru.yandex.metrika.api.management.client.utils.MessengerValidator;
import ru.yandex.metrika.api.management.client.utils.SocialNetworkValidator;
import ru.yandex.metrika.autogoals.AutoGoals;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.schedulerd.tests.SchedulerdBaseTest;
import ru.yandex.metrika.util.ApiInputValidator;
import ru.yandex.metrika.util.PropertyUtilsMysql;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

import static java.util.Map.entry;

@ParametersAreNonnullByDefault
public abstract class AbstractAutogoalsCreatorTest extends SchedulerdBaseTest {
    @ClassRule
    public static final SpringClassRule scr = new SpringClassRule();

    @Rule
    public final SpringMethodRule smr = new SpringMethodRule();

    @Autowired
    protected AutogoalsCreator autogoalsCreator;

    @Autowired
    protected GoalsService goalsService;

    @Autowired
    protected MySqlJdbcTemplate countersTemplate;

    @Autowired
    protected PartnersGoalsDao partnersGoalsDao;

    static final List<String> partnersGoalsExactActionsList = List.of(
            "Jivo_Client_initiate_chat",
            "Jivo_Proactive_invitation_accepted",
            "Jivo_Client_answer_on_agent_request",
            "Jivo_Offline_message_sent",
            "ym-subscription-confirm",
            "ym-new-income-form-confirm",
            "ym-order-form-product-confirm",
            "ym-order-form-service-confirm",
            "ym-one-click-form-confirm",
            "ym-feedback-form-confirm",
            "ym-callback-form-confirm",
            "ym-lead-form-confirm",
            "ym-page-cart",
            "ym-page-checkout",
            "ym-page-pay",
            "ym-open-leadform",
            "ym-get-response",
            "ym-contact-constractor",
            "ym-open-chat",
            "ym-send-message",
            "ym-show-contacts",
            "ym-agree-constractor",
            "ym-complete-order",
            "ym-agree-meeting",
            "ym-start-course",
            "ym-confirm-contact",
            "ym-create-resume",
            "ym-send-resume",
            "ym-successful-lead",
            "ym-login"
    );

    // action from CH.hits-all -> action from partner_goals and ad_goals_urls
    static final Map<String, String> partnersGoalsRegexpActionsMap = Map.ofEntries(
            entry("ym-submit-leadform", "^ym\\-submit\\-lead(?:\\-[0-9]+|form)?$"),
            entry("ym-register", "^ym\\-register(?:\\-[0-9]+)?$"),
            entry("ym-submit-contact-1","^ym\\-submit\\-contact(?:\\-[0-9]+|s)?$"),
            entry("ym-add-payment-info-2222","^ym\\-add\\-payment\\-info(?:\\-[0-9]+)?$"),
            entry("ym-add-to-cart-3","^ym\\-add\\-to\\-cart(?:\\-[0-9]+)?$"),
            entry("ym-add-to-wishlist-44","^ym\\-add\\-to\\-wishlist(?:\\-[0-9]+)?$"),
            entry("ym-begin-checkout", "^ym\\-begin\\-checkout(?:\\-[0-9]+)?$"),
            entry("ym-subscribe","^ym\\-subscribe(?:\\-[0-9]+)?$"),
            entry("ym-purchase-7890","^ym\\-purchase(?:\\-[0-9]+)?$"),
            entry("ololo-ym-metrika-test", "ym\\-metrika") // проверка метода find() у Matcher
    );

    static final List<String> allPartnerAutogoalsToTest =
            Stream.of(partnersGoalsExactActionsList, partnersGoalsRegexpActionsMap.keySet())
            .flatMap(Collection::stream)
            .toList();

    static final Map<String, String> renamedPartnersGoalsRegexpActionsMap = partnersGoalsRegexpActionsMap.keySet().stream()
            .collect(Collectors.toMap(hitsAtcion -> hitsAtcion.replaceFirst("ym-", ""),
                    hitsAction -> partnersGoalsRegexpActionsMap.get(hitsAction).replaceFirst("ym\\\\-", "")));

    private static final Set<Integer> ignoredTypes = Set.of(
            6, // PURCHASE - пока не сделано, под вопросом
            8, // PARTNER - отдельные тесты
            11, 12 // A_CART, A_PURCHASE - отдельные тесты
    );

    static final int limit = AutoGoals.Type.values().length - 1; //all types in a row minus UNDEFINED

    protected static int getCounterIdWithEnabledAutogoals() {
        return 42;
    }

    protected static int getCounterIdWithDisabledAutogoals() {
        return 43;
    }

    protected static Set<Integer> getIgnoredTypes() {
        return ignoredTypes;
    }

    protected void markAllGoalsAsDeleted(int counterId) {
        goalsService.deleteAll(counterId);
    }

    protected void cleanAllGoals(int counterId) {
        //здесь бы ещё по-хорошему чистить ad_goals_urls, но кому это надо, вы ещё предложите память за собой руками очищать, лол.
        countersTemplate.update("DELETE FROM ad_goals WHERE counter_id = ?", counterId);
    }

    @Configuration
    @ImportResource(locations = {
            "/ru/yandex/metrika/schedulerd/steps/schedulerd-steps.xml",
            "/ru/yandex/metrika/util/common-jmx-support.xml",
            "/ru/yandex/metrika/util/common-jdbc.xml",
    })
    public static class AutogoalsConfig {

        @Bean
        public AutogoalsCreator autogoalsCreator(LocaleDictionaries localeDictionaries, GoalsService goalsService,
                                                 MySqlJdbcTemplate countersTemplate, PartnersGoalsDao partnersGoalsDao) {
            AutogoalsCreator autogoalsCreator = new AutogoalsCreator(localeDictionaries, goalsService, countersTemplate, partnersGoalsDao);
            autogoalsCreator.setContactDataGoalsEnabled(true);
            autogoalsCreator.setLoginWithYandexCIDGoalsEnabled(true);
            return autogoalsCreator;
        }

        @Bean
        public LocaleDictionaries localeDictionaries() {
            return new LocaleDictionaries();
        }

        @Bean
        public GoalsService goalsService(MySqlJdbcTemplate countersTemplate,
                                         ApiInputValidator validator,
                                         CounterLimitsService counterLimitsService,
                                         LocaleDictionaries dictionaries,
                                         FormGoalsService formGoalsService) {
            var goalsService = new GoalsService();
            goalsService.setValidator(validator);
            goalsService.setJdbcTemplate(countersTemplate);
            goalsService.setCounterLimitsService(counterLimitsService);
            goalsService.setDictionaries(dictionaries);
            goalsService.setFormGoalsService(formGoalsService);

            PropertyUtilsMysql propertyUtils = new PropertyUtilsMysql();
            propertyUtils.setPropertiesDb(countersTemplate);
            propertyUtils.afterPropertiesSet();

            GoalIdGenerationService goalIdGenerationService = new GoalIdGenerationService();
            goalIdGenerationService.setConvMain(countersTemplate);

            goalsService.setGoalIdGenerationService(goalIdGenerationService);
            return goalsService;
        }

        @Bean
        public FormGoalsService formGoalsService() {
            return counterIds -> {};
        }

        @Bean
        public CounterLimitsService counterLimitsService() {
            return new DefaultCounterLimitsService();
        }

        @Bean
        public ApiInputValidator apiInputValidator(Validator validator, LocaleDictionaries localeDictionaries) {
            return new ApiInputValidator(validator, localeDictionaries);
        }

        @Bean
        public PartnersGoalsDao partnersGoalsDao(MySqlJdbcTemplate countersTemplate) {
            var partnersGoalsDao = new PartnersGoalsDao();
            partnersGoalsDao.setConvMain(countersTemplate);
            return partnersGoalsDao;
        }

        @Bean
        public Validator validator() {
            return new LocalValidatorFactoryBean();
        }

        @Bean
        public MessengerService messengerService(MySqlJdbcTemplate countersTemplate) {
            return new MessengerService(countersTemplate);
        }

        @Bean
        public MessengerValidator messengerValidator(MessengerService messengerService) {
            return new MessengerValidator(messengerService);
        }

        @Bean
        public GoalConditionValidator goalConditionValidator() {
            return new GoalConditionValidator();
        }

        @Bean
        public SocialNetworkValidator socialNetworkValidator(SocialNetworkService socialNetworkService){
            return  new SocialNetworkValidator(socialNetworkService);
        }

        @Bean
        public SocialNetworkService socialNetworkService(MySqlJdbcTemplate countersTemplate) {
            return new SocialNetworkService(countersTemplate);
        }
    }
}
