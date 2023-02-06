package ru.yandex.metrika.api.management.tests.medium.client;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Random;
import java.util.Set;
import java.util.stream.Collectors;

import org.apache.commons.lang3.StringUtils;
import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.api.ApiException;
import ru.yandex.metrika.api.error.LimitException;
import ru.yandex.metrika.api.error.ValidationException;
import ru.yandex.metrika.api.management.client.GoalIdGenerationService;
import ru.yandex.metrika.api.management.client.GoalsService;
import ru.yandex.metrika.api.management.client.GoalsTransformer;
import ru.yandex.metrika.api.management.client.counter.CounterOptionsService;
import ru.yandex.metrika.api.management.client.external.goals.ACartGoal;
import ru.yandex.metrika.api.management.client.external.goals.APurchaseGoal;
import ru.yandex.metrika.api.management.client.external.goals.ActionGoal;
import ru.yandex.metrika.api.management.client.external.goals.ButtonGoal;
import ru.yandex.metrika.api.management.client.external.goals.CallGoal;
import ru.yandex.metrika.api.management.client.external.goals.CartGoal;
import ru.yandex.metrika.api.management.client.external.goals.CdpGoals;
import ru.yandex.metrika.api.management.client.external.goals.CdpOrderInProgressGoal;
import ru.yandex.metrika.api.management.client.external.goals.CdpOrderPaidGoal;
import ru.yandex.metrika.api.management.client.external.goals.CompositeGoal;
import ru.yandex.metrika.api.management.client.external.goals.ConditionalGoal;
import ru.yandex.metrika.api.management.client.external.goals.FileGoal;
import ru.yandex.metrika.api.management.client.external.goals.GoalCondition;
import ru.yandex.metrika.api.management.client.external.goals.GoalConditionOperator;
import ru.yandex.metrika.api.management.client.external.goals.GoalConditionType;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.goals.GoalMarketType;
import ru.yandex.metrika.api.management.client.external.goals.GoalSource;
import ru.yandex.metrika.api.management.client.external.goals.GoalStatus;
import ru.yandex.metrika.api.management.client.external.goals.GoalType;
import ru.yandex.metrika.api.management.client.external.goals.MessengerGoal;
import ru.yandex.metrika.api.management.client.external.goals.OfflineGoal;
import ru.yandex.metrika.api.management.client.external.goals.PaymentSystemGoal;
import ru.yandex.metrika.api.management.client.external.goals.PhoneGoal;
import ru.yandex.metrika.api.management.client.external.goals.PurchaseGoal;
import ru.yandex.metrika.api.management.client.external.goals.SiteSearchGoal;
import ru.yandex.metrika.api.management.client.external.goals.SocialNetworkGoal;
import ru.yandex.metrika.api.management.client.external.goals.UrlGoal;
import ru.yandex.metrika.api.management.client.external.goals.call.CallGoalCondition;
import ru.yandex.metrika.api.management.client.external.goals.call.CallGoalField;
import ru.yandex.metrika.api.management.client.external.goals.call.ConditionalCallGoal;
import ru.yandex.metrika.api.management.client.model.DatabaseGoal;
import ru.yandex.metrika.api.management.client.model.DatabaseGoalCondition;
import ru.yandex.metrika.api.management.config.ApiValidatorConfig;
import ru.yandex.metrika.api.management.config.CounterOptionsServiceConfig;
import ru.yandex.metrika.api.management.config.JdbcTemplateConfig;
import ru.yandex.metrika.api.management.config.LocaleDictionariesConfig;
import ru.yandex.metrika.api.management.config.MessengerValidatorConfig;
import ru.yandex.metrika.api.management.config.SocialNetworkValidatorConfig;
import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.test.matchers.MoreMatchers;
import ru.yandex.metrika.util.ApiInputValidator;
import ru.yandex.metrika.util.PropertyUtilsMysql;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

import static ru.yandex.metrika.api.management.client.GoalsService.HIDDEN_PHONES_SEPARATOR;
import static ru.yandex.metrika.api.management.client.GoalsService.HIDDEN_PHONES_WILDCARD;
import static ru.yandex.metrika.api.management.client.GoalsTransformer.equalIgnoreFields;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class GoalsServiceTest {
    @Autowired
    private GoalsService goalsService;

    @Autowired
    private MySqlJdbcTemplate convMainTemplate;

    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
    }

    @Rule
    public ExpectedException exception = ExpectedException.none();

    @Test
    public void createFileGoalTest() {
        int counterId = createCounter();

        List<GoalCondition> messengerGoalConditions = List.of(
                new GoalCondition(GoalConditionType.file, "file.png", 0)
        );

        FileGoal fileGoal = new FileGoal(
                0, counterId, "Цель по скачиванию файлов", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, messengerGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        GoalE goal = goalsService.create(counterId, fileGoal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());

        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals("Цель по скачиванию файлов", dbGoal.getName());
        Assert.assertEquals(GoalType.file, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());

        List<DatabaseGoalCondition> goalConditions = getGoalConditionsQuery(goal.getId());

        Assert.assertEquals(1, goalConditions.size());

        DatabaseGoalCondition goalCondition = goalConditions.get(0);

        Assert.assertEquals(goal.getId(), goalCondition.getGoalId());
        Assert.assertEquals(1, goalCondition.getSerial());
        Assert.assertEquals(GoalConditionType.file.name(), goalCondition.getPatternType());
        Assert.assertEquals("file.png", goalCondition.getUrl());
    }

    @Test
    public void createFileGoalWithConditionTypeAllFilesTest() {
        int counterId = createCounter();

        List<GoalCondition> messengerGoalConditions = List.of(
                new GoalCondition(GoalConditionType.all_files, "", 0)
        );

        FileGoal fileGoal = new FileGoal(
                0, counterId, "Цель по скачиванию любого файла", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, messengerGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        GoalE goal = goalsService.create(counterId, fileGoal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());

        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals("Цель по скачиванию любого файла", dbGoal.getName());
        Assert.assertEquals(GoalType.file, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());

        List<DatabaseGoalCondition> goalConditions = getGoalConditionsQuery(goal.getId());

        Assert.assertEquals(1, goalConditions.size());

        DatabaseGoalCondition goalCondition = goalConditions.get(0);

        Assert.assertEquals(goal.getId(), goalCondition.getGoalId());
        Assert.assertEquals(1, goalCondition.getSerial());
        Assert.assertEquals(GoalConditionType.all_files.name(), goalCondition.getPatternType());
        Assert.assertEquals("", goalCondition.getUrl());
    }

    @Test
    public void tryToCreateFileGoalWithConditionTypeAllFilesAndWithNotEmptyConditionUrlTest() {
        int counterId = createCounter();

        List<GoalCondition> messengerGoalConditions = List.of(
                new GoalCondition(GoalConditionType.all_files, "aaa", 0)
        );

        FileGoal fileGoal = new FileGoal(
                0, counterId, "Цель по скачиванию любого файла", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, messengerGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        exception.expect(ValidationException.class);

        goalsService.create(counterId, fileGoal);
    }

    @Test
    public void tryToCreateFileGoalWithoutGoalCondition() {
        int counterId = createCounter();
        FileGoal fileGoal = new FileGoal(
                0, counterId, "Цель по скачиванию файлов", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, new ArrayList<>(), false, 1, 100, GoalSource.user, false, null
        );

        exception.expect(ApiException.class);
        exception.expectMessage("Цель \"Скачивание файла\" должна иметь хотя бы одно условие достижения");

        goalsService.create(counterId, fileGoal);
    }

    @Test
    public void tryToCreateFileGoalWithMoreThanOneGoalCondition() {
        List<GoalCondition> messengerGoalConditions = Arrays.asList(
                new GoalCondition(GoalConditionType.file, "file_1.png", 0),
                new GoalCondition(GoalConditionType.contain, "file_2.jpg", 0)
        );

        int counterId = createCounter();
        FileGoal fileGoal = new FileGoal(
                0, counterId, "Цель по скачиванию файлов", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, messengerGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        exception.expect(ApiException.class);
        exception.expectMessage("Выберите условие \"Любой файл\" или один конкретный файл");

        goalsService.create(counterId, fileGoal);
    }

    @Test
    public void createPaymentSystemGoalTest() {
        int counterId = createCounter();
        PaymentSystemGoal paymentSystemGoal = new PaymentSystemGoal(
                0, counterId, "Цель платежные системы", new Date(System.currentTimeMillis()), 0, false, 1,
                GoalSource.user, false, null
        );
        GoalE goal = goalsService.create(counterId, paymentSystemGoal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());

        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals("Цель платежные системы", dbGoal.getName());
        Assert.assertEquals(GoalType.payment_system, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());
        Assert.assertEquals(GoalSource.user, dbGoal.getGoalSource());
    }

    @Test
    public void createSiteSearchGoalTest() {
        int counterId = createCounter();

        List<GoalCondition> siteSearchGoalConditions = List.of(
                new GoalCondition(GoalConditionType.search, "search,query,text", 0)
        );

        SiteSearchGoal siteSearchGoal = new SiteSearchGoal(
                0, counterId, "Цель: Поиск по сайту", new Date(System.currentTimeMillis()), 0.0,
                GoalMarketType.empty, siteSearchGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        GoalE goal = goalsService.create(counterId, siteSearchGoal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());

        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals("Цель: Поиск по сайту", dbGoal.getName());
        Assert.assertEquals(GoalType.search, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());

        List<DatabaseGoalCondition> goalConditions = getGoalConditionsQuery(goal.getId());

        Assert.assertEquals(1, goalConditions.size());

        DatabaseGoalCondition goalCondition = goalConditions.get(0);

        Assert.assertEquals(goal.getId(), goalCondition.getGoalId());
        Assert.assertEquals(1, goalCondition.getSerial());
        Assert.assertEquals(GoalConditionType.search.name(), goalCondition.getPatternType());
        Assert.assertEquals("search,query,text", goalCondition.getUrl());
    }

    @Test
    public void createSiteSearchGoalWithExtraSpacesInUrlTest() {
        int counterId = createCounter();

        List<GoalCondition> siteSearchGoalConditions = List.of(
                new GoalCondition(GoalConditionType.search, "  search   ,    query,    text   ", 0)
        );

        SiteSearchGoal siteSearchGoal = new SiteSearchGoal(
                0, counterId, "Цель: Поиск по сайту 2", new Date(System.currentTimeMillis()), 0.0,
                GoalMarketType.empty, siteSearchGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        GoalE goal = goalsService.create(counterId, siteSearchGoal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());

        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals("Цель: Поиск по сайту 2", dbGoal.getName());
        Assert.assertEquals(GoalType.search, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());

        List<DatabaseGoalCondition> goalConditions = getGoalConditionsQuery(goal.getId());

        Assert.assertEquals(1, goalConditions.size());

        DatabaseGoalCondition goalCondition = goalConditions.get(0);

        Assert.assertEquals(goal.getId(), goalCondition.getGoalId());
        Assert.assertEquals(1, goalCondition.getSerial());
        Assert.assertEquals(GoalConditionType.search.name(), goalCondition.getPatternType());
        Assert.assertEquals("search,query,text", goalCondition.getUrl());
    }

    @Test
    public void tryToCreateSiteSearchGoalWithoutGoalConditionsTest() {
        int counterId = createCounter();

        List<GoalCondition> siteSearchGoalConditions = Collections.emptyList();

        SiteSearchGoal siteSearchGoal = new SiteSearchGoal(
                0, counterId, "Цель: Поиск по сайту", new Date(System.currentTimeMillis()), 0.0,
                GoalMarketType.empty, siteSearchGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        exception.expect(ApiException.class);
        exception.expectMessage("Цель \"Поиск по сайту\" должна иметь хотя бы одно условие достижения");

        goalsService.create(counterId, siteSearchGoal);
    }

    @Test
    public void tryToCreateSiteSearchGoalWithMultipleGoalConditionsTest() {
        int counterId = createCounter();

        List<GoalCondition> siteSearchGoalConditions = Arrays.asList(
                new GoalCondition(GoalConditionType.search, "search,query,text", 0),
                new GoalCondition(GoalConditionType.exact, "blablabla", 0)
        );

        SiteSearchGoal siteSearchGoal = new SiteSearchGoal(
                0, counterId, "Цель: Поиск по сайту", new Date(System.currentTimeMillis()), 0.0, GoalMarketType.empty,
                siteSearchGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        exception.expect(ApiException.class);
        exception.expectMessage("Ровно одно условие должно быть у цели \"Поиск по сайту\"");

        goalsService.create(counterId, siteSearchGoal);
    }

    @Test
    public void tryToCreateSiteSearchGoalWithWrongGoalConditionTest() {
        int counterId = createCounter();

        List<GoalCondition> siteSearchGoalConditions = List.of(
                new GoalCondition(GoalConditionType.exact, "blablabla", 0)
        );

        SiteSearchGoal siteSearchGoal = new SiteSearchGoal(
                0, counterId, "Цель: Поиск по сайту", new Date(System.currentTimeMillis()), 0.0, GoalMarketType.empty,
                siteSearchGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        exception.expect(ApiException.class);
        exception.expectMessage("Цель search не может иметь условие типа exact");

        goalsService.create(counterId, siteSearchGoal);
    }

    @Test
    public void createButtonGoalTest() {
        int counterId = createCounter();

        List<GoalCondition> messengerGoalConditions = Arrays.asList(
                new GoalCondition(GoalConditionType.btn_type, "url_1", 0),
                new GoalCondition(GoalConditionType.btn_content, "url_2", 0)
        );

        ButtonGoal buttonGoal = new ButtonGoal(
                0, counterId, "Цель клик по кнопке", new Date(System.currentTimeMillis()), 0.0, GoalMarketType.empty,
                messengerGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        GoalE goal = goalsService.create(counterId, buttonGoal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());

        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals("Цель клик по кнопке", dbGoal.getName());
        Assert.assertEquals(GoalType.button, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());

        List<DatabaseGoalCondition> goalConditions = getGoalConditionsQuery(goal.getId());

        Assert.assertEquals(2, goalConditions.size());

        DatabaseGoalCondition goalConditionBtnType = goalConditions.get(0);
        DatabaseGoalCondition goalConditionBtnContent = goalConditions.get(1);

        Assert.assertEquals(goal.getId(), goalConditionBtnType.getGoalId());
        Assert.assertEquals(1, goalConditionBtnType.getSerial());
        Assert.assertEquals(GoalConditionType.btn_type.name(), goalConditionBtnType.getPatternType());
        Assert.assertEquals("url_1", goalConditionBtnType.getUrl());

        Assert.assertEquals(goal.getId(), goalConditionBtnContent.getGoalId());
        Assert.assertEquals(2, goalConditionBtnContent.getSerial());
        Assert.assertEquals(GoalConditionType.btn_content.name(), goalConditionBtnContent.getPatternType());
        Assert.assertEquals("url_2", goalConditionBtnContent.getUrl());

        Assert.assertEquals(isButtonGoalExist(counterId), true);
    }

    @Test
    public void tryToCreateButtonGoalWithEmptyConditionUrlTest() {
        int counterId = createCounter();

        List<GoalCondition> messengerGoalConditions = Arrays.asList(
                new GoalCondition(GoalConditionType.btn_href, "", 0),
                new GoalCondition(GoalConditionType.btn_content, null, 0)
        );

        ButtonGoal buttonGoal = new ButtonGoal(
                0, counterId, "Цель клик по кнопке", new Date(System.currentTimeMillis()), 0.0, GoalMarketType.empty,
                messengerGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        exception.expect(ValidationException.class);

        goalsService.create(counterId, buttonGoal);
    }

    @Test
    public void tryToCreateButtonGoalWithoutGoalCondition() {
        int counterId = createCounter();
        ButtonGoal buttonGoal = new ButtonGoal(
                0, counterId, "Цель клик по кнопке", new Date(System.currentTimeMillis()), 0.0, GoalMarketType.empty,
                new ArrayList<>(), false, 1, 100, GoalSource.user, false, null
        );

        exception.expect(ApiException.class);
        exception.expectMessage("Цель \"Клик по кнопке\" должна иметь хотя бы одно условие достижения");

        goalsService.create(counterId, buttonGoal);
    }

    @Test
    public void createMessengerGoalTest() {
        int counterId = createCounter();

        List<GoalCondition> messengerGoalConditions = List.of(
                new GoalCondition(GoalConditionType.messenger, "whatsapp", 0)
        );

        MessengerGoal messengerGoal = new MessengerGoal(
                0, counterId, "Цель по переходам в месседжер", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, messengerGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        GoalE goal = goalsService.create(counterId, messengerGoal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());

        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals("Цель по переходам в месседжер", dbGoal.getName());
        Assert.assertEquals(GoalType.messenger, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());

        List<DatabaseGoalCondition> goalConditions = getGoalConditionsQuery(goal.getId());

        Assert.assertEquals(1, goalConditions.size());

        DatabaseGoalCondition goalCondition = goalConditions.get(0);

        Assert.assertEquals(goal.getId(), goalCondition.getGoalId());
        Assert.assertEquals(1, goalCondition.getSerial());
        Assert.assertEquals(GoalConditionType.messenger.name(), goalCondition.getPatternType());
        Assert.assertEquals("whatsapp", goalCondition.getUrl());
    }

    @Test
    public void createMessengerGoalWithTypeAllMessengersTest() {
        int counterId = createCounter();

        List<GoalCondition> messengerGoalConditions = List.of(
                new GoalCondition(GoalConditionType.messenger, "all_messengers", 0)
        );

        MessengerGoal messengerGoal = new MessengerGoal(
                0, counterId, "Цель по переходам в месседжер", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, messengerGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        GoalE goal = goalsService.create(counterId, messengerGoal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());

        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals("Цель по переходам в месседжер", dbGoal.getName());
        Assert.assertEquals(GoalType.messenger, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());

        List<DatabaseGoalCondition> goalConditions = getGoalConditionsQuery(goal.getId());

        Assert.assertEquals(1, goalConditions.size());

        DatabaseGoalCondition goalCondition = goalConditions.get(0);

        Assert.assertEquals(goal.getId(), goalCondition.getGoalId());
        Assert.assertEquals(1, goalCondition.getSerial());
        Assert.assertEquals(GoalConditionType.messenger.name(), goalCondition.getPatternType());
        Assert.assertEquals("all_messengers", goalCondition.getUrl());
    }

    @Test
    public void tryToCreateMessengerGoalWithNoGoalConditions() {
        int counterId = createCounter();
        MessengerGoal messengerGoal = new MessengerGoal(
                0, counterId, "Цель по переходам в месседжер", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, new ArrayList<>(), false, 1, 100, GoalSource.user, false, null
        );

        exception.expect(ApiException.class);
        exception.expectMessage("Цель \"Переход в мессенджер\" должна иметь хотя бы одно условие достижения");

        goalsService.create(counterId, messengerGoal);
    }

    @Test
    public void tryToCreateMessengerGoalWithMoreThanOneGoalCondition() {
        List<GoalCondition> messengerGoalConditions = Arrays.asList(
                new GoalCondition(GoalConditionType.messenger, "whatsapp", 0),
                new GoalCondition(GoalConditionType.messenger, "telegram", 0)
        );

        int counterId = createCounter();
        MessengerGoal messengerGoal = new MessengerGoal(
                0, counterId, "Цель по переходам в месседжер", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, messengerGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        exception.expect(ApiException.class);
        exception.expectMessage("Выберите условие \"Все мессенджеры\" или один конкретный мессенджер");

        goalsService.create(counterId, messengerGoal);
    }

    @Test
    public void tryToCreateMessengerGoalWithGoalConditionsThatContainAllMessengersTypeAndTelegramType() {
        List<GoalCondition> messengerGoalConditions = Arrays.asList(
                new GoalCondition(GoalConditionType.messenger, "all_messengers", 0),
                new GoalCondition(GoalConditionType.messenger, "telegram", 0)
        );

        int counterId = createCounter();
        MessengerGoal messengerGoal = new MessengerGoal(
                0, counterId, "Цель по переходам в месседжер", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, messengerGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        exception.expect(ApiException.class);
        exception.expectMessage("Выберите условие \"Все мессенджеры\" или один конкретный мессенджер");

        goalsService.create(counterId, messengerGoal);
    }

    @Test
    public void createMessengerGoalWithWrongGoalConditionType() {
        int counterId = createCounter();

        List<GoalCondition> messengerGoalConditions = List.of(
                new GoalCondition(GoalConditionType.exact, "whatsapp", 0)
        );

        MessengerGoal messengerGoal = new MessengerGoal(
                0, counterId, "Цель по переходам в месседжер", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, messengerGoalConditions, false, 1, 0, GoalSource.user, false, null
        );

        exception.expect(ApiException.class);
        exception.expectMessage("Цель messenger не может иметь условие типа exact");

        goalsService.create(counterId, messengerGoal);
    }

    @Test
    public void createMessengerGoalWithWrongGoalConditionValue() {
        int counterId = createCounter();

        List<GoalCondition> messengerGoalConditions = List.of(
                new GoalCondition(GoalConditionType.messenger, "blablabla", 0)
        );

        MessengerGoal messengerGoal = new MessengerGoal(
                0, counterId, "Цель по переходам в месседжер", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, messengerGoalConditions, false, 1, 0, GoalSource.user, false, null
        );

        exception.expect(ValidationException.class);

        goalsService.create(counterId, messengerGoal);
    }

    @Test
    public void createSocialNetworkGoalTest() {
        int counterId = createCounter();

        List<GoalCondition> socialNetworkGoalConditions = List.of(
                new GoalCondition(GoalConditionType.social, "vkontakte", 0)
        );

        SocialNetworkGoal socialNetworkGoal = new SocialNetworkGoal(
                0, counterId, "Цель: переход в социальные сети", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, socialNetworkGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        GoalE goal = goalsService.create(counterId, socialNetworkGoal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());

        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals("Цель: переход в социальные сети", dbGoal.getName());
        Assert.assertEquals(GoalType.social, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());

        List<DatabaseGoalCondition> goalConditions = getGoalConditionsQuery(goal.getId());

        Assert.assertEquals(1, goalConditions.size());

        DatabaseGoalCondition goalCondition = goalConditions.get(0);

        Assert.assertEquals(goal.getId(), goalCondition.getGoalId());
        Assert.assertEquals(1, goalCondition.getSerial());
        Assert.assertEquals(GoalConditionType.social.name(), goalCondition.getPatternType());
        Assert.assertEquals("vkontakte", goalCondition.getUrl());
    }

    @Test
    public void createSocialNetworkGoalWithTypeAllSocialTest() {
        int counterId = createCounter();

        List<GoalCondition> socialNetworkGoalConditions = List.of(
                new GoalCondition(GoalConditionType.all_social, "", 0)
        );

        SocialNetworkGoal socialNetworkGoal = new SocialNetworkGoal(
                0, counterId, "Цель: переход в социальные сети", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, socialNetworkGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        GoalE goal = goalsService.create(counterId, socialNetworkGoal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());

        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals("Цель: переход в социальные сети", dbGoal.getName());
        Assert.assertEquals(GoalType.social, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());

        List<DatabaseGoalCondition> goalConditions = getGoalConditionsQuery(goal.getId());

        Assert.assertEquals(1, goalConditions.size());

        DatabaseGoalCondition goalCondition = goalConditions.get(0);

        Assert.assertEquals(goal.getId(), goalCondition.getGoalId());
        Assert.assertEquals(1, goalCondition.getSerial());
        Assert.assertEquals(GoalConditionType.all_social.name(), goalCondition.getPatternType());
        Assert.assertEquals("", goalCondition.getUrl());
    }

    @Test
    public void tryToCreateSocialNetworkGoalWithGoalConditionsAllSocialAndSocialVkontakte() {
        List<GoalCondition> socialNetworkGoalConditions = Arrays.asList(
                new GoalCondition(GoalConditionType.all_social, "", 0),
                new GoalCondition(GoalConditionType.social, "vkontakte", 0)
        );

        int counterId = createCounter();
        SocialNetworkGoal socialNetworkGoal = new SocialNetworkGoal(
                0, counterId, "Цель по переходам в месседжер", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, socialNetworkGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        exception.expect(ApiException.class);
        exception.expectMessage("Выберите условие \"Все социальные сети\" или одну конкретную социальную сеть");

        goalsService.create(counterId, socialNetworkGoal);
    }

    @Test
    public void tryToCreateSocialNetworkGoalWithGoalConditionTypeAllSocialButContainsWrongGoalConditionValue() {
        List<GoalCondition> socialNetworkGoalConditions = List.of(
                new GoalCondition(GoalConditionType.all_social, "blablabla", 0)
        );

        int counterId = createCounter();
        SocialNetworkGoal socialNetworkGoal = new SocialNetworkGoal(
                0, counterId, "Цель: переход в социальные сети", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, socialNetworkGoalConditions, false, 1, 0, GoalSource.user, false, null
        );

        exception.expect(ValidationException.class);

        goalsService.create(counterId, socialNetworkGoal);
    }

    @Test
    public void tryToCreateSocialNetworkGoalWithNoGoalConditions() {
        int counterId = createCounter();
        SocialNetworkGoal socialNetworkGoal = new SocialNetworkGoal(
                0, counterId, "Цель: переход в социальные сети", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, new ArrayList<>(), false, 1, 100, GoalSource.user, false, null
        );

        exception.expect(ApiException.class);
        exception.expectMessage("Цель \"Переход в социальные сети\" должна иметь хотя бы одно условие достижения");

        goalsService.create(counterId, socialNetworkGoal);
    }

    @Test
    public void tryToCreateSocialNetworkGoalWithMoreThanOneGoalCondition() {
        List<GoalCondition> socialNetworkGoalConditions = Arrays.asList(
                new GoalCondition(GoalConditionType.social, "vkontakte", 0),
                new GoalCondition(GoalConditionType.social, "twitter", 0)
        );

        int counterId = createCounter();
        SocialNetworkGoal socialNetworkGoal = new SocialNetworkGoal(
                0, counterId, "Цель: переход в социальные сети", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, socialNetworkGoalConditions, false, 1, 100, GoalSource.user, false, null
        );

        exception.expect(ApiException.class);
        exception.expectMessage("Выберите условие \"Все социальные сети\" или одну конкретную социальную сеть");

        goalsService.create(counterId, socialNetworkGoal);
    }

    @Test
    public void createSocialNetworkGoalWithWrongGoalConditionType() {
        int counterId = createCounter();

        List<GoalCondition> socialNetworkGoalConditions = List.of(
                new GoalCondition(GoalConditionType.exact, "vkontakte", 0)
        );

        SocialNetworkGoal socialNetworkGoal = new SocialNetworkGoal(
                0, counterId, "Цель: переход в социальные сети", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, socialNetworkGoalConditions, false, 1, 0, GoalSource.user, false, null
        );

        exception.expect(ApiException.class);
        exception.expectMessage("Цель social не может иметь условие типа exact");

        goalsService.create(counterId, socialNetworkGoal);
    }

    @Test
    public void createSocialNetworkGoalWithWrongGoalConditionValue() {
        int counterId = createCounter();

        List<GoalCondition> socialNetworkGoalConditions = List.of(
                new GoalCondition(GoalConditionType.social, "blablabla", 0)
        );

        SocialNetworkGoal socialNetworkGoal = new SocialNetworkGoal(
                0, counterId, "Цель: переход в социальные сети", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, socialNetworkGoalConditions, false, 1, 0, GoalSource.user, false, null
        );

        exception.expect(ValidationException.class);

        goalsService.create(counterId, socialNetworkGoal);
    }


    @Test
    public void createCdpGoalsTest() {
        int counterId = createCounter();

        CdpGoals cdpGoals = goalsService.cdpGoals(counterId);

        long cdpOrderInProgressGoalId = cdpGoals.getCdpOrderInProgressGoalId();
        long cdpOrderPaidGoalId = cdpGoals.getCdpOrderPaidGoalId();

        DatabaseGoal cdpOrderInProgressGoal = getGoalByGoalIdQuery(counterId, cdpOrderInProgressGoalId);
        DatabaseGoal cdpOrderPaidGoal = getGoalByGoalIdQuery(counterId, cdpOrderPaidGoalId);

        Assert.assertEquals(GoalStatus.Active, cdpOrderInProgressGoal.getStatus());
        Assert.assertEquals(cdpGoals.getCdpOrderInProgressGoalId(), cdpOrderInProgressGoalId);
        Assert.assertEquals("CRM: Заказ создан", cdpOrderInProgressGoal.getName());

        Assert.assertEquals(GoalStatus.Active, cdpOrderPaidGoal.getStatus());
        Assert.assertEquals(cdpGoals.getCdpOrderPaidGoalId(), cdpOrderPaidGoalId);
        Assert.assertEquals("CRM: Заказ оплачен", cdpOrderPaidGoal.getName());
    }

    @Test
    public void reviveCdpGoalsTest() {
        int counterId = createCounter();

        CdpGoals cdpGoals = goalsService.cdpGoals(counterId);

        long cdpOrderInProgressGoalId = cdpGoals.getCdpOrderInProgressGoalId();
        long cdpOrderPaidGoalId = cdpGoals.getCdpOrderPaidGoalId();

        deleteGoal(counterId, cdpOrderInProgressGoalId);
        deleteGoal(counterId, cdpOrderPaidGoalId);

        DatabaseGoal cdpOrderInProgressGoal = getGoalByGoalIdQuery(counterId, cdpOrderInProgressGoalId);
        DatabaseGoal cdpOrderPaidGoal = getGoalByGoalIdQuery(counterId, cdpOrderPaidGoalId);

        Assert.assertEquals(GoalStatus.Deleted, cdpOrderInProgressGoal.getStatus());
        Assert.assertEquals(GoalStatus.Deleted, cdpOrderPaidGoal.getStatus());

        goalsService.cdpGoals(counterId);

        cdpOrderInProgressGoal = getGoalByGoalIdQuery(counterId, cdpOrderInProgressGoalId);
        cdpOrderPaidGoal = getGoalByGoalIdQuery(counterId, cdpOrderPaidGoalId);

        Assert.assertEquals(GoalStatus.Active, cdpOrderInProgressGoal.getStatus());
        Assert.assertEquals(cdpGoals.getCdpOrderInProgressGoalId(), cdpOrderInProgressGoalId);
        Assert.assertEquals("CRM: Заказ создан", cdpOrderInProgressGoal.getName());

        Assert.assertEquals(GoalStatus.Active, cdpOrderPaidGoal.getStatus());
        Assert.assertEquals(cdpGoals.getCdpOrderPaidGoalId(), cdpOrderPaidGoalId);
        Assert.assertEquals("CRM: Заказ оплачен", cdpOrderPaidGoal.getName());
    }

    @Test
    public void reviveCdpOrderInProgressGoal() {
        int counterId = createCounter();

        CdpGoals cdpGoals = goalsService.cdpGoals(counterId);

        long cdpOrderInProgressGoalId = cdpGoals.getCdpOrderInProgressGoalId();
        long cdpOrderPaidGoalId = cdpGoals.getCdpOrderPaidGoalId();

        deleteGoal(counterId, cdpOrderInProgressGoalId);

        DatabaseGoal cdpOrderInProgressGoal = getGoalByGoalIdQuery(counterId, cdpOrderInProgressGoalId);
        DatabaseGoal cdpOrderPaidGoal = getGoalByGoalIdQuery(counterId, cdpOrderPaidGoalId);

        Assert.assertEquals(GoalStatus.Deleted, cdpOrderInProgressGoal.getStatus());
        Assert.assertEquals(GoalStatus.Active, cdpOrderPaidGoal.getStatus());

        goalsService.cdpGoals(counterId);

        cdpOrderInProgressGoal = getGoalByGoalIdQuery(counterId, cdpOrderInProgressGoalId);
        cdpOrderPaidGoal = getGoalByGoalIdQuery(counterId, cdpOrderPaidGoalId);

        Assert.assertEquals(GoalStatus.Active, cdpOrderInProgressGoal.getStatus());
        Assert.assertEquals(cdpGoals.getCdpOrderInProgressGoalId(), cdpOrderInProgressGoalId);
        Assert.assertEquals("CRM: Заказ создан", cdpOrderInProgressGoal.getName());

        Assert.assertEquals(GoalStatus.Active, cdpOrderPaidGoal.getStatus());
        Assert.assertEquals(cdpGoals.getCdpOrderPaidGoalId(), cdpOrderPaidGoalId);
        Assert.assertEquals("CRM: Заказ оплачен", cdpOrderPaidGoal.getName());
    }

    @Test
    public void reviveCdpOrderPaidGoal() {
        int counterId = createCounter();

        CdpGoals cdpGoals = goalsService.cdpGoals(counterId);

        long cdpOrderInProgressGoalId = cdpGoals.getCdpOrderInProgressGoalId();
        long cdpOrderPaidGoalId = cdpGoals.getCdpOrderPaidGoalId();

        deleteGoal(counterId, cdpOrderPaidGoalId);

        DatabaseGoal cdpOrderInProgressGoal = getGoalByGoalIdQuery(counterId, cdpOrderInProgressGoalId);
        DatabaseGoal cdpOrderPaidGoal = getGoalByGoalIdQuery(counterId, cdpOrderPaidGoalId);

        Assert.assertEquals(GoalStatus.Active, cdpOrderInProgressGoal.getStatus());
        Assert.assertEquals(GoalStatus.Deleted, cdpOrderPaidGoal.getStatus());

        goalsService.cdpGoals(counterId);

        cdpOrderInProgressGoal = getGoalByGoalIdQuery(counterId, cdpOrderInProgressGoalId);
        cdpOrderPaidGoal = getGoalByGoalIdQuery(counterId, cdpOrderPaidGoalId);

        Assert.assertEquals(GoalStatus.Active, cdpOrderInProgressGoal.getStatus());
        Assert.assertEquals(cdpGoals.getCdpOrderInProgressGoalId(), cdpOrderInProgressGoalId);
        Assert.assertEquals("CRM: Заказ создан", cdpOrderInProgressGoal.getName());

        Assert.assertEquals(GoalStatus.Active, cdpOrderPaidGoal.getStatus());
        Assert.assertEquals(cdpGoals.getCdpOrderPaidGoalId(), cdpOrderPaidGoalId);
        Assert.assertEquals("CRM: Заказ оплачен", cdpOrderPaidGoal.getName());
    }

    @Test
    public void tryToCreateCallGoalThroughGoalsServiceCreateMethod() {
        int counterId = createCounter();

        CallGoal goal = new CallGoal(0, counterId, "test name",
                new Date(System.currentTimeMillis()), 0, true,
                1, GoalSource.user, false, null);

        exception.expect(ApiException.class);
        exception.expectMessage("Недопустимый тип цели.");
        goalsService.create(counterId, goal);
    }

    @Test
    public void createCartGoalTest() {
        int counterId = createCounter();
        CartGoal cartGoal = new CartGoal(0, counterId, "Ecommerce: добавление в корзину", new Date(), 0, false, 1, GoalSource.auto, false, null);

        //it's not so simple to create and then get Hidden goal =)
        goalsService.createGoalsForCounters(Map.of(counterId, List.of(cartGoal)));
        GoalE goal = goalsService.findByCounterIds(List.of(counterId), false, false, true).get(counterId).get(0);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());

        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals(cartGoal.getName(), dbGoal.getName());
        Assert.assertEquals(GoalType.e_cart, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());
        Assert.assertEquals(GoalStatus.Hidden, dbGoal.getStatus());

        List<DatabaseGoalCondition> goalConditions = getGoalConditionsQuery(goal.getId());
        Assert.assertEquals(0, goalConditions.size());
    }

    @Test
    public void createPurchaseGoalTest() {
        goalsService.setEPurchaseGoalsEnabled(true);
        int counterId = createCounter();
        var purchaseGoal = new PurchaseGoal(0, counterId, "Ecommerce: покупка", new Date(), 0, false, 1, GoalSource.auto, false, null);

        //it's not so simple to create and then get Hidden goal =)
        goalsService.createGoalsForCounters(Map.of(counterId, List.of(purchaseGoal)));

        GoalE goal = goalsService.findByCounterIds(List.of(counterId), false, false, true).get(counterId).get(0);

        DatabaseGoal dbGoal = getGoalsByCounterId(counterId).get(0);

        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals(purchaseGoal.getName(), dbGoal.getName());
        Assert.assertEquals(GoalType.e_purchase, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());
        Assert.assertEquals(GoalStatus.Hidden, dbGoal.getStatus());

        List<DatabaseGoalCondition> goalConditions = getGoalConditionsQuery(goal.getId());
        Assert.assertEquals(0, goalConditions.size());
    }

    @Test
    public void createACartGoalTest() {
        int counterId = createCounter();
        ACartGoal goal = new ACartGoal(0, counterId, "createACartGoalTest", new Date(), 0, false, 1, GoalSource.auto, false, null);

        GoalE created = goalsService.create(counterId, goal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), created.getId());

        Assert.assertEquals(created.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals(created.getName(), dbGoal.getName());
        Assert.assertEquals(GoalType.a_cart, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());
        Assert.assertEquals(GoalStatus.Active, dbGoal.getStatus());

        List<DatabaseGoalCondition> goalConditions = getGoalConditionsQuery(created.getId());
        Assert.assertEquals(0, goalConditions.size());
    }

    @Test
    public void sovetnikForbiddenAutogoalsTest() {
        int counterIdACart = createCounter();
        int counterIdAPurchaseGoal = createCounter();

        ACartGoal aCartGoal = new ACartGoal(0, counterIdACart, "createACartGoalTest", new Date(), 0, false, 1, GoalSource.auto, false, null);
        APurchaseGoal aPurchaseGoal = new APurchaseGoal(2, counterIdAPurchaseGoal, "createAPurchaseGoalTest", new Date(), 0, false, 1, GoalSource.auto, false, null);

        goalsService.create(counterIdACart, aCartGoal);
        goalsService.create(counterIdAPurchaseGoal, aPurchaseGoal);

        Assert.assertEquals(Set.of(GoalType.a_cart),
                goalsService.getForbiddenToCreateAutogoals(Set.of(counterIdACart))
                        .get(counterIdACart).getGoalTypes()
        );
        Assert.assertEquals(Set.of(GoalType.a_purchase),
                goalsService.getForbiddenToCreateAutogoals(Set.of(counterIdAPurchaseGoal))
                        .get(counterIdAPurchaseGoal).getGoalTypes()
        );
    }

    @Test
    public void sovetnikForbiddenECartAutogoalsTest() {
        int counterId = createCounter();

        var eCartGoal = new CartGoal(0, counterId, "createECartGoalTest", new Date(), 0, false, 1, GoalSource.auto, false, null);

        goalsService.createGoalsForCounters(Map.of(counterId, List.of(eCartGoal)));

        Assert.assertEquals(Set.of(GoalType.a_purchase, GoalType.a_cart, GoalType.e_cart),
                goalsService.getForbiddenToCreateAutogoals(Set.of(counterId)).get(counterId).getGoalTypes()
        );
    }

    @Test
    public void sovetnikForbiddenEPurchaseAutogoalsTest() {
        int counterId = createCounter();

        var ePurchaseGoal = new PurchaseGoal(0, counterId, "createEPurchaseGoalTest", new Date(), 0, false, 1, GoalSource.auto, false, null);

        goalsService.createGoalsForCounters(Map.of(counterId, List.of(ePurchaseGoal)));

        Assert.assertEquals(Set.of(GoalType.a_purchase, GoalType.a_cart, GoalType.e_purchase),
                goalsService.getForbiddenToCreateAutogoals(Set.of(counterId)).get(counterId).getGoalTypes()
        );
    }

    @Test
    public void sovetnikAllAutogoalsAllowedTest() {
        int counterId = createCounter();

        var offlineGoal = createOfflineGoal(counterId);

        goalsService.createGoalsForCounters(Map.of(counterId, List.of(offlineGoal)));

        Assert.assertEquals(Set.of(GoalType.offline),
                goalsService.getForbiddenToCreateAutogoals(Set.of(counterId)).get(counterId).getGoalTypes()
        );
    }

    @Test
    public void createAPurchaseGoalTest() {
        int counterId = createCounter();
        APurchaseGoal goal = new APurchaseGoal(0, counterId, "createAPurchaseGoalTest", new Date(), 0, false, 1, GoalSource.auto, false, null);

        GoalE created = goalsService.create(counterId, goal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), created.getId());

        Assert.assertEquals(created.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals(created.getName(), dbGoal.getName());
        Assert.assertEquals(GoalType.a_purchase, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());
        Assert.assertEquals(GoalStatus.Active, dbGoal.getStatus());

        List<DatabaseGoalCondition> goalConditions = getGoalConditionsQuery(created.getId());
        Assert.assertEquals(0, goalConditions.size());
    }

    @Test
    public void tryToCreateACartUserGoalTest() {
        int counterId = createCounter();
        ACartGoal goal = new ACartGoal(0, counterId, "tryToCreateACartUserGoalTest", new Date(), 0, false, 1, GoalSource.user, false, null);
        exception.expect(ApiException.class);
        exception.expectMessage("Недопустимый тип цели.");
        goalsService.create(counterId, goal);
    }

    @Test
    public void tryToCreateAPurchaseUserGoalTest() {
        int counterId = createCounter();
        APurchaseGoal goal = new APurchaseGoal(0, counterId, "tryToCreateAPurchaseUserGoalTest", new Date(), 0, false, 1, GoalSource.user, false, null);
        exception.expect(ApiException.class);
        exception.expectMessage("Недопустимый тип цели.");
        goalsService.create(counterId, goal);
    }

    @Test
    public void tryToCreateCdpOrderInProgressGoalThroughGoalsServiceCreateMethod() {
        int counterId = createCounter();

        var goal = new CdpOrderInProgressGoal(0, counterId, "test name",
                new Date(System.currentTimeMillis()), 0, true,
                1, GoalSource.user, false, null);

        exception.expect(ApiException.class);
        exception.expectMessage("Недопустимый тип цели.");
        goalsService.create(counterId, goal);
    }

    @Test
    public void tryToCreateCdpOrderPaidGoalThroughGoalsServiceCreateMethod() {
        int counterId = createCounter();

        var goal = new CdpOrderPaidGoal(0, counterId, "test name", new Date(System.currentTimeMillis()),
                0, true, 1, GoalSource.user, false, null);

        exception.expect(ApiException.class);
        exception.expectMessage("Недопустимый тип цели.");
        goalsService.create(counterId, goal);
    }

    @Test
    public void createGoalWithGoalSourceAuto() {
        int counterId = createCounter();

        List<GoalCondition> messengerGoalConditions = List.of(
                new GoalCondition(GoalConditionType.file, "filename.png", 0)
        );

        FileGoal fileGoal = new FileGoal(
                0, counterId, "Цель по скачиванию файлов", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, messengerGoalConditions, false, 1, 100, GoalSource.auto, false, null
        );

        GoalE goal = goalsService.create(counterId, fileGoal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());

        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals("Цель по скачиванию файлов", dbGoal.getName());
        Assert.assertEquals(GoalType.file, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());
        Assert.assertEquals(GoalSource.auto, dbGoal.getGoalSource());

        List<DatabaseGoalCondition> goalConditions = getGoalConditionsQuery(goal.getId());

        Assert.assertEquals(1, goalConditions.size());

        DatabaseGoalCondition goalCondition = goalConditions.get(0);

        Assert.assertEquals(goal.getId(), goalCondition.getGoalId());
        Assert.assertEquals(1, goalCondition.getSerial());
        Assert.assertEquals(GoalConditionType.file.name(), goalCondition.getPatternType());
        Assert.assertEquals("filename.png", goalCondition.getUrl());
    }

    @Test
    public void notUpdateAutoGoal() {
        int counterId = createCounter();

        List<GoalCondition> messengerGoalConditions = List.of(
                new GoalCondition(GoalConditionType.file, "filename.png", 0)
        );

        FileGoal fileGoal = new FileGoal(
                0, counterId, "Цель по скачиванию файлов", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, messengerGoalConditions, false, 0, 0, GoalSource.auto, false, null
        );

        GoalE goal = goalsService.create(counterId, fileGoal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());
        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals("Цель по скачиванию файлов", dbGoal.getName());
        Assert.assertEquals(GoalType.file, dbGoal.getType());
        Assert.assertEquals(GoalSource.auto, dbGoal.getGoalSource());

        ((ConditionalGoal) goal).getConditions().get(0).setGoalId(0);
        ((ConditionalGoal) goal).getConditions().get(0).setSerial(0);
        GoalE notUpdatedGoal = goalsService.update(counterId, goal.getId(), goal);

        DatabaseGoal notUpdatedDbGoal = getGoalByGoalIdQuery(notUpdatedGoal.getCounterId(), notUpdatedGoal.getId());
        Assert.assertEquals(goal.getId(), notUpdatedDbGoal.getGoalId());
        Assert.assertEquals(counterId, notUpdatedDbGoal.getCounterId());
        Assert.assertEquals("Цель по скачиванию файлов", notUpdatedDbGoal.getName());
        Assert.assertEquals(GoalType.file, notUpdatedDbGoal.getType());
        Assert.assertEquals(GoalSource.auto, notUpdatedDbGoal.getGoalSource());
        Assert.assertTrue(equalIgnoreFields(((FileGoal) goal).getConditions(), ((FileGoal) notUpdatedGoal).getConditions()));
    }

    @Test
    public void setGoalsMethodTest() {
        int counterId = createCounter();

        List<GoalCondition> fileGoalConditions = List.of(
                new GoalCondition(GoalConditionType.file, "filename.png", 0)
        );

        FileGoal fileGoal = new FileGoal(
                0, counterId, "Цель по скачиванию файлов", new Date(System.currentTimeMillis()), 0,
                GoalMarketType.empty, fileGoalConditions, false, 1, 100, GoalSource.auto, false, null
        );

        List<GoalE> goals = goalsService.setGoals(counterId, List.of(fileGoal));

        Assert.assertEquals(goals.size(), 1);

        GoalE goal = goals.get(0);

        List<DatabaseGoalCondition> goalConditions = getGoalConditionsQuery(goal.getId());

        DatabaseGoalCondition goalCondition = goalConditions.get(0);

        Assert.assertEquals(goal.getId(), goalCondition.getGoalId());
        Assert.assertEquals(1, goalCondition.getSerial());
        Assert.assertEquals(GoalConditionType.file.name(), goalCondition.getPatternType());
        Assert.assertEquals("filename.png", goalCondition.getUrl());
    }

    @Test
    public void tryToCreateALotOfGoalsOnCounter() {
        int counterId = createCounter();

        var listOfGoals = new ArrayList<GoalE>();
        for (int i = 0; i < 200; i++) {
            listOfGoals.add(createPhoneGoal(counterId));
        }
        goalsService.createGoalsForCounters(Map.of(counterId, listOfGoals));

        exception.expect(LimitException.class);
        exception.expectMessage("Превышен лимит целей.");

        goalsService.createGoalsForCounters(Map.of(counterId, List.of(createPhoneGoal(counterId))));
    }

    @Test
    public void tryToCreateSeveralOfOfflineGoalsOnCounter() {
        int counterId = createCounter();

        var listOfGoals = new ArrayList<GoalE>();
        for (int i = 0; i < 2; i++) {
            listOfGoals.add(createOfflineGoal(counterId));
        }
        exception.expect(LimitException.class);
        exception.expectMessage("Превышен лимит offline целей.");

        goalsService.createGoalsForCounters(Map.of(counterId, listOfGoals));
    }

    @Test
    public void createPhoneGoalWithHidePhoneTest() {
        int counterId = createCounter();
        PhoneGoal goal = createPhoneGoal(counterId, true);

        GoalE created = goalsService.create(counterId, goal);

        Assert.assertEquals(0, (int) created.getSerial());
        Assert.assertEquals(GoalType.phone, created.getType());
        Assert.assertTrue(((PhoneGoal) created).getHidePhoneNumber());
        Assert.assertEquals(1, ((PhoneGoal) created).getConditions().size());
        Assert.assertEquals(GoalConditionType.exact, ((PhoneGoal) created).getConditions().get(0).getOperator());

        Set<String> hiddenPhones = getHiddenPhonesAsSet(counterId);
        Assert.assertEquals(1, hiddenPhones.size());
        Assert.assertTrue(hiddenPhones.contains(clipLeadingPlus(goal.getConditions().get(0).getValue())));
    }

    @Test
    public void createPhoneGoalWithoutHidePhoneTest() {
        int counterId = createCounter();
        PhoneGoal goal = createPhoneGoal(counterId, false);

        GoalE created = goalsService.create(counterId, goal);

        Assert.assertEquals(0, (int) created.getSerial());
        Assert.assertEquals(GoalType.phone, created.getType());
        Assert.assertFalse(((PhoneGoal) created).getHidePhoneNumber());
        Assert.assertEquals(1, ((PhoneGoal) created).getConditions().size());
        Assert.assertEquals(GoalConditionType.exact, ((PhoneGoal) created).getConditions().get(0).getOperator());

        Set<String> hiddenPhones = getHiddenPhonesAsSet(counterId);
        Assert.assertTrue(hiddenPhones.isEmpty());
    }

    @Test
    public void createPhoneGoalWithoutHidePhone2Test() {
        int counterId = createCounter();
        PhoneGoal goal = createPhoneGoal(counterId);

        GoalE created = goalsService.create(counterId, goal);

        Assert.assertEquals(0, (int) created.getSerial());
        Assert.assertEquals(GoalType.phone, created.getType());
        Assert.assertFalse(((PhoneGoal) created).getHidePhoneNumber());
        Assert.assertEquals(1, ((PhoneGoal) created).getConditions().size());
        Assert.assertEquals(GoalConditionType.exact, ((PhoneGoal) created).getConditions().get(0).getOperator());

        Set<String> hiddenPhones = getHiddenPhonesAsSet(counterId);
        Assert.assertTrue(hiddenPhones.isEmpty());
    }

    @Test
    public void updateHiddenPhoneGoalHidePhoneTest() {
        int counterId = createCounter();
        PhoneGoal goal = createPhoneGoal(counterId);

        GoalE created = goalsService.create(counterId, goal);
        Set<String> hiddenPhones1 = getHiddenPhonesAsSet(counterId);
        Assert.assertTrue(hiddenPhones1.isEmpty());
        Assert.assertFalse(((PhoneGoal) goalsService.findById(counterId, created.getId())).getHidePhoneNumber());

        ((PhoneGoal) created).setHidePhoneNumber(true);
        goalsService.update(counterId, created.getId(), created);

        Set<String> hiddenPhones2 = getHiddenPhonesAsSet(counterId);
        Assert.assertEquals(1, hiddenPhones2.size());
        Assert.assertEquals(
                hiddenPhones2,
                Set.of(
                        clipLeadingPlus(goal.getConditions().get(0).getValue())
                )
        );
        Assert.assertTrue(((PhoneGoal) goalsService.findById(counterId, created.getId())).getHidePhoneNumber());
    }

    @Test
    public void updateHiddenPhoneGoalChangePhoneTest() {
        int counterId = createCounter();
        PhoneGoal goal1 = createPhoneGoal(counterId, true);
        PhoneGoal goal2 = createPhoneGoal(counterId, true);

        GoalE created1 = goalsService.create(counterId, goal1);
        GoalE created2 = goalsService.create(counterId, goal2);

        ((PhoneGoal) created2).getConditions().get(0).setValue("+70000000000");

        goalsService.update(counterId, created2.getId(), created2);

        Set<String> hiddenPhones = getHiddenPhonesAsSet(counterId);
        Assert.assertEquals(2, hiddenPhones.size());
        Assert.assertEquals(
                hiddenPhones,
                Set.of(
                        clipLeadingPlus(((PhoneGoal) created1).getConditions().get(0).getValue()),
                        "70000000000"
                )
        );
    }

    @Test
    public void updateHiddenPhoneGoalUnhidePhoneTest() {
        int counterId = createCounter();
        PhoneGoal goal1 = createPhoneGoal(counterId, true);
        PhoneGoal goal2 = createPhoneGoal(counterId, true);

        GoalE created1 = goalsService.create(counterId, goal1);
        GoalE created2 = goalsService.create(counterId, goal2);

        Assert.assertTrue(((PhoneGoal) goalsService.findById(counterId, created1.getId())).getHidePhoneNumber());
        Assert.assertTrue(((PhoneGoal) goalsService.findById(counterId, created2.getId())).getHidePhoneNumber());

        ((PhoneGoal) created2).setHidePhoneNumber(false);

        goalsService.update(counterId, created2.getId(), created2);

        Set<String> hiddenPhones = getHiddenPhonesAsSet(counterId);
        Assert.assertEquals(1, hiddenPhones.size());
        Assert.assertEquals(
                hiddenPhones,
                Set.of(
                        clipLeadingPlus(((PhoneGoal) created1).getConditions().get(0).getValue())
                )
        );
        Assert.assertFalse(((PhoneGoal) goalsService.findById(counterId, created2.getId())).getHidePhoneNumber());
    }

    @Test
    public void updateHiddenPhoneGoalChangeNameTest() {
        int counterId = createCounter();
        PhoneGoal goal1 = createPhoneGoal(counterId, true);
        PhoneGoal goal2 = createPhoneGoal(counterId, true);

        GoalE created1 = goalsService.create(counterId, goal1);
        GoalE created2 = goalsService.create(counterId, goal2);

        created2.setName("updated_" + created2.getName());

        goalsService.update(counterId, created2.getId(), created2);

        Set<String> hiddenPhones = getHiddenPhonesAsSet(counterId);
        Assert.assertEquals(2, hiddenPhones.size());
        Assert.assertEquals(
                hiddenPhones,
                Set.of(
                        clipLeadingPlus(((PhoneGoal) created1).getConditions().get(0).getValue()),
                        clipLeadingPlus(((PhoneGoal) created2).getConditions().get(0).getValue())
                )
        );
    }

    @Test
    public void deleteHiddenPhoneGoalTest() {
        int counterId = createCounter();
        PhoneGoal goal1 = createPhoneGoal(counterId, true);
        GoalE created1 = goalsService.create(counterId, goal1);

        goalsService.delete(counterId, created1.getId());

        Set<String> hiddenPhones = getHiddenPhonesAsSet(counterId);
        Assert.assertTrue(hiddenPhones.isEmpty());
    }

    @Test
    public void deleteAllHiddenPhoneGoalTest() {
        int counterId = createCounter();

        PhoneGoal goal1 = createPhoneGoal(counterId, true);
        PhoneGoal goal2 = createPhoneGoal(counterId, true);
        PhoneGoal goal3 = createPhoneGoal(counterId, false);

        GoalE created1 = goalsService.create(counterId, goal1);
        GoalE created2 = goalsService.create(counterId, goal2);
        GoalE created3 = goalsService.create(counterId, goal3);

        Set<String> hiddenPhones = getHiddenPhonesAsSet(counterId);
        Assert.assertEquals(2, hiddenPhones.size());
        Assert.assertEquals(
                hiddenPhones,
                Set.of(
                        clipLeadingPlus(((PhoneGoal) created1).getConditions().get(0).getValue()),
                        clipLeadingPlus(((PhoneGoal) created2).getConditions().get(0).getValue())
                )
        );

        goalsService.deleteAll(counterId);

        hiddenPhones = getHiddenPhonesAsSet(counterId);
        Assert.assertTrue(hiddenPhones.isEmpty());
    }

    @Test
    public void createHiddenPhoneGoalListMethodTest() {
        int counterId = createCounter();
        PhoneGoal goal1 = createPhoneGoal(counterId, true);
        PhoneGoal goal2 = createPhoneGoal(counterId, true);
        PhoneGoal goal3 = createPhoneGoal(counterId, false);

        goalsService.create(counterId, List.of(goal1, goal2, goal3));

        Set<String> hiddenPhones = getHiddenPhonesAsSet(counterId);
        Assert.assertEquals(2, hiddenPhones.size());
        Assert.assertEquals(
                hiddenPhones,
                Set.of(
                        clipLeadingPlus(goal1.getConditions().get(0).getValue()),
                        clipLeadingPlus(goal2.getConditions().get(0).getValue())
                )
        );
    }

    @Test
    public void createHiddenPhoneGoalForSeveralCounters() {
        int counterId1 = createCounter();
        PhoneGoal goal11 = createPhoneGoal(counterId1, true);
        PhoneGoal goal12 = createPhoneGoal(counterId1, true);
        PhoneGoal goal13 = createPhoneGoal(counterId1, false);

        int counterId2 = createCounter();
        PhoneGoal goal21 = createPhoneGoal(counterId1, false);
        PhoneGoal goal22 = createPhoneGoal(counterId1, true);

        goalsService.createGoalsForCounters(
                Map.of(
                        counterId1, List.of(goal11, goal12, goal13),
                        counterId2, List.of(goal21, goal22)
                )
        );

        Set<String> hiddenPhones1 = getHiddenPhonesAsSet(counterId1);
        Assert.assertEquals(2, hiddenPhones1.size());
        Assert.assertEquals(
                hiddenPhones1,
                Set.of(
                        clipLeadingPlus(goal11.getConditions().get(0).getValue()),
                        clipLeadingPlus(goal12.getConditions().get(0).getValue())
                )
        );

        Set<String> hiddenPhones2 = getHiddenPhonesAsSet(counterId2);
        Assert.assertEquals(1, hiddenPhones2.size());
        Assert.assertEquals(
                hiddenPhones2,
                Set.of(
                        clipLeadingPlus(goal22.getConditions().get(0).getValue())
                )
        );
    }

    @Test
    public void mergeHiddenPhoneGoalsTest() {
        int counterId = createCounter();
        PhoneGoal goal1 = createPhoneGoal(counterId, true);
        PhoneGoal goal2 = createPhoneGoal(counterId, true);
        PhoneGoal goal3 = createPhoneGoal(counterId, true);
        PhoneGoal goal4 = createPhoneGoal(counterId, true);

        List<GoalE> created = goalsService.create(counterId, List.of(goal1, goal2, goal3));

        Set<String> hiddenPhones = getHiddenPhonesAsSet(counterId);
        Assert.assertEquals(3, hiddenPhones.size());
        Assert.assertEquals(
                hiddenPhones,
                Set.of(
                        clipLeadingPlus(goal1.getConditions().get(0).getValue()),
                        clipLeadingPlus(goal2.getConditions().get(0).getValue()),
                        clipLeadingPlus(goal3.getConditions().get(0).getValue())
                )
        );

        ((PhoneGoal) created.get(0)).getConditions().get(0).setValue("+00000000000");
        ((PhoneGoal) created.get(1)).setHidePhoneNumber(false);
        created.remove(2);
        created.add(goal4);

        List<GoalE> updated = goalsService.setGoals(counterId, created);
        Assert.assertEquals(3, updated.size());

        hiddenPhones = getHiddenPhonesAsSet(counterId);
        Assert.assertEquals(2, hiddenPhones.size());
        Assert.assertEquals(
                hiddenPhones,
                Set.of(
                        "00000000000",
                        clipLeadingPlus(goal4.getConditions().get(0).getValue())
                )
        );
    }

    @Test
    public void hiddenPhoneGoalFilterNumbersTest() {
        int counterId = createCounter();
        PhoneGoal goal1 = createPhoneGoal(counterId, true);
        goal1.getConditions().get(0).setValue("+70000000001");
        PhoneGoal goal2 = createPhoneGoal(counterId, true);
        goal2.getConditions().get(0).setValue("pref+700000substr00002suf");
        PhoneGoal goal3 = createPhoneGoal(counterId, true);
        goal3.getConditions().get(0).setValue("not numeric characters");

        goalsService.create(counterId, List.of(goal1, goal2, goal3));

        Set<String> hiddenPhones = getHiddenPhonesAsSet(counterId);
        Assert.assertEquals(2, hiddenPhones.size());
        Assert.assertEquals(
                hiddenPhones,
                Set.of(
                        "70000000001",
                        "70000000002"
                )
        );
    }

    @Test
    public void identicalHiddenPhoneGoalsTest() {
        int counterId = createCounter();
        PhoneGoal goal1 = createPhoneGoal(counterId, true);
        goal1.getConditions().clear();
        PhoneGoal goal2 = createPhoneGoal(counterId, true);
        goal2.getConditions().clear();
        PhoneGoal goal3 = createPhoneGoal(counterId, true);
        goal3.getConditions().clear();
        PhoneGoal goal4 = createPhoneGoal(counterId, true);
        goal4.getConditions().clear();

        List<GoalE> created = goalsService.create(counterId, List.of(goal1, goal2, goal3));

        Map<String, Integer> hiddenPhones = getHiddenPhonesAsMap(counterId);
        Assert.assertTrue(hiddenPhones.containsKey(HIDDEN_PHONES_WILDCARD));
        Assert.assertEquals(3, (int) hiddenPhones.get(HIDDEN_PHONES_WILDCARD));

        ((PhoneGoal) created.get(0)).setHidePhoneNumber(false);
        GoalCondition condition = new GoalCondition();
        condition.setOperator(GoalConditionType.exact);
        condition.setValue("+70000000000");
        ((PhoneGoal) created.get(1)).setConditions(
                Collections.singletonList(
                        condition
                )
        );

        goalsService.update(counterId, created.get(0).getId(), created.get(0));
        goalsService.update(counterId, created.get(1).getId(), created.get(1));

        hiddenPhones = getHiddenPhonesAsMap(counterId);
        Assert.assertTrue(hiddenPhones.containsKey(HIDDEN_PHONES_WILDCARD));
        Assert.assertEquals(1, (int) hiddenPhones.get(HIDDEN_PHONES_WILDCARD));
        Assert.assertEquals(1, (int) hiddenPhones.get("70000000000"));

        goalsService.create(counterId, goal4);

        hiddenPhones = getHiddenPhonesAsMap(counterId);
        Assert.assertTrue(hiddenPhones.containsKey(HIDDEN_PHONES_WILDCARD));
        Assert.assertEquals(2, (int) hiddenPhones.get(HIDDEN_PHONES_WILDCARD));
        Assert.assertEquals(1, (int) hiddenPhones.get("70000000000"));

        goalsService.delete(counterId, created.get(2).getId());
        hiddenPhones = getHiddenPhonesAsMap(counterId);
        Assert.assertTrue(hiddenPhones.containsKey(HIDDEN_PHONES_WILDCARD));
        Assert.assertEquals(1, (int) hiddenPhones.get(HIDDEN_PHONES_WILDCARD));
        Assert.assertEquals(1, (int) hiddenPhones.get("70000000000"));
    }

    @Test
    public void tryToCreateTooLongPhoneNumberGoalTest() {
        int counterId = createCounter();
        PhoneGoal goal = createPhoneGoal(counterId, true);
        goal.getConditions().get(0).setValue("123456789101112131415161718");

        exception.expect(ApiException.class);

        goalsService.create(counterId, goal);
    }

    @Test
    public void updateHiddenPhoneGoalChangeNumberToWildCard() {
        int counterId = createCounter();
        PhoneGoal goal = createPhoneGoal(counterId, true);

        GoalE created = goalsService.create(counterId, goal);

        Set<String> hiddenPhones = getHiddenPhonesAsSet(counterId);
        Assert.assertEquals(1, hiddenPhones.size());
        Assert.assertEquals(
                hiddenPhones,
                Set.of(
                        clipLeadingPlus(goal.getConditions().get(0).getValue())
                )
        );

        ((PhoneGoal) created).setConditions(Collections.emptyList());

        goalsService.update(counterId, created.getId(), created);
        hiddenPhones = getHiddenPhonesAsSet(counterId);
        Assert.assertEquals(1, hiddenPhones.size());
        Assert.assertEquals(
                hiddenPhones,
                Set.of(
                        HIDDEN_PHONES_WILDCARD
                )
        );
    }

    @Test
    public void createHiddenPhoneGoalAlphabetNumberTest() {
        int counterId = createCounter();
        PhoneGoal goal = createPhoneGoal(counterId, true);
        goal.getConditions().get(0).setValue("letters");

        goalsService.create(counterId, goal);

        Set<String> hiddenPhones = getHiddenPhonesAsSet(counterId);
        Assert.assertEquals(0, hiddenPhones.size());
    }

    private PhoneGoal createPhoneGoal(Integer counterId, Boolean hiddenNumber) {
        PhoneGoal goal = createPhoneGoal(counterId);
        goal.setHidePhoneNumber(hiddenNumber);
        return goal;
    }

    @Test
    public void createConditionalCallGoal() {
        int counterId = createCounter();

        List<CallGoalCondition> conditions = List.of(
                new CallGoalCondition(CallGoalField.call_missed, GoalConditionOperator.exact, "true", 0, 0),
                new CallGoalCondition(CallGoalField.call_duration, GoalConditionOperator.between, "5|30", 0, 0),
                new CallGoalCondition(CallGoalField.call_first, GoalConditionOperator.exact, "false", 0, 0),
                new CallGoalCondition(CallGoalField.call_tag, GoalConditionOperator.start, "label", 0, 0)
        );

        ConditionalCallGoal conditionalCallGoal = new ConditionalCallGoal(
                0, counterId, "Цель: Звонок", new Date(System.currentTimeMillis()), 0, conditions, false, 0,
                GoalSource.user, false, null
        );

        GoalE goal = goalsService.create(counterId, conditionalCallGoal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());

        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals("Цель: Звонок", dbGoal.getName());
        Assert.assertEquals(GoalType.conditional_call, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());

        List<DatabaseGoalCondition> goalConditions = getGoalConditionsQuery(goal.getId());

        Assert.assertEquals(4, goalConditions.size());

        for (DatabaseGoalCondition condition : goalConditions) {
            Assert.assertEquals(goal.getId(), condition.getGoalId());

            CallGoalCondition cond = (CallGoalCondition) GoalsTransformer.conditionByGoalType(GoalType.conditional_call, condition);
            switch (cond.getField()) {
                case call_first -> Assert.assertEquals("false", condition.getUrl());
                case call_missed -> Assert.assertEquals("true", condition.getUrl());
                case call_duration -> Assert.assertEquals("5|30", condition.getUrl());
                case call_tag -> Assert.assertEquals("label", condition.getUrl());
                default -> throw new AssertionError(condition.getPatternType() + " is unknown type");
            }
        }
    }

    @Test
    public void createConditionalCallGoalWithoutConditions() {
        int counterId = createCounter();

        ConditionalCallGoal conditionalCallGoal = new ConditionalCallGoal(
                0, counterId, "Цель: Звонок", new Date(System.currentTimeMillis()), 0, List.of(), false, 0,
                GoalSource.user, false, null
        );

        GoalE goal = goalsService.create(counterId, conditionalCallGoal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());

        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals("Цель: Звонок", dbGoal.getName());
        Assert.assertEquals(GoalType.conditional_call, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());
        Assert.assertTrue(dbGoal.getConditions() == null || dbGoal.getConditions().isEmpty());
    }

    @Test
    public void updateConditionalCallGoal() {
        int counterId = createCounter();

        CallGoalCondition condition = new CallGoalCondition(CallGoalField.call_missed, GoalConditionOperator.exact, "true", 0, 0);
        ConditionalCallGoal conditionalCallGoal = new ConditionalCallGoal(
                0, counterId, "Цель: Звонок", new Date(System.currentTimeMillis()), 0, List.of(condition), false, 0,
                GoalSource.user, false, null
        );

        GoalE goal = goalsService.create(counterId, conditionalCallGoal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());
        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals("Цель: Звонок", dbGoal.getName());
        Assert.assertEquals(GoalType.conditional_call, dbGoal.getType());
        Assert.assertEquals(0, dbGoal.getDepth());
        Assert.assertEquals(0, dbGoal.getSerial());
        Assert.assertEquals(0, dbGoal.getPrevGoalId());

        List<DatabaseGoalCondition> dbCondition = getGoalConditionsQuery(goal.getId());
        Assert.assertEquals(1, dbCondition.size());
        Assert.assertEquals(CallGoalField.call_missed.name(), dbCondition.get(0).getField());
        Assert.assertEquals(GoalConditionOperator.exact.name(), dbCondition.get(0).getPatternType());
        Assert.assertEquals("true", dbCondition.get(0).getUrl());

        CallGoalCondition conditionUpdate = new CallGoalCondition(CallGoalField.call_duration, GoalConditionOperator.between, "5|30", 0, 0);
        ((ConditionalCallGoal) goal).setConditions(List.of(conditionUpdate));
        goalsService.update(counterId, goal.getId(), goal);

        DatabaseGoal dbGoal2 = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());
        Assert.assertEquals(goal.getId(), dbGoal2.getGoalId());
        Assert.assertEquals(counterId, dbGoal2.getCounterId());

        List<DatabaseGoalCondition> dbCondition2 = getGoalConditionsQuery(goal.getId());
        Assert.assertEquals(1, dbCondition2.size());
        Assert.assertEquals(conditionUpdate.getField().name(), dbCondition2.get(0).getField());
        Assert.assertEquals(conditionUpdate.getOperator().name(), dbCondition2.get(0).getPatternType());
        Assert.assertEquals(conditionUpdate.getValue(), dbCondition2.get(0).getUrl());
    }

    @Test
    public void tryToCreateCallGoalConditionTagInvalidValue() {
        int counterId = createCounter();

        CallGoalCondition condition = new CallGoalCondition(CallGoalField.call_first, GoalConditionOperator.contain, "true", 0, 0);
        ConditionalCallGoal goal = new ConditionalCallGoal(0, counterId, "test name",
                new Date(System.currentTimeMillis()), 0, List.of(condition), false, 0, GoalSource.user, false, null);

        exception.expect(ApiException.class);
        exception.expectMessage("call_first не может иметь условие типа contain");
        goalsService.create(counterId, goal);
    }

    @Test
    public void tryToCreateCallGoalDuplicateCondition() {
        int counterId = createCounter();

        CallGoalCondition condition1 = new CallGoalCondition(CallGoalField.call_first, GoalConditionOperator.exact, "true", 0, 0);
        CallGoalCondition condition2 = new CallGoalCondition(CallGoalField.call_first, GoalConditionOperator.exact, "true", 0, 0);
        ConditionalCallGoal goal = new ConditionalCallGoal(0, counterId, "test name",
                new Date(System.currentTimeMillis()), 0, List.of(condition1, condition2), false, 0, GoalSource.user, false, null);

        exception.expect(ApiException.class);
        exception.expectMessage("Цель \"Звонок\" не может иметь более 1 условия для call_first");
        goalsService.create(counterId, goal);
    }

    @Test
    public void tryToCreateCallGoalConditionMissedInvalidValue() {
        int counterId = createCounter();

        CallGoalCondition condition = new CallGoalCondition(CallGoalField.call_missed, GoalConditionOperator.exact, "1", 0, 0);
        ConditionalCallGoal goal = new ConditionalCallGoal(0, counterId, "test name",
                new Date(System.currentTimeMillis()), 0, List.of(condition), false, 0, GoalSource.user, false, null);

        exception.expect(ApiException.class);
        exception.expectMessage("1 недопустимое значение. Используйте `true` или `false`");
        goalsService.create(counterId, goal);
    }

    @Test
    public void tryToCreateCallGoalConditionTagInvalidOperator() {
        int counterId = createCounter();

        CallGoalCondition condition = new CallGoalCondition(CallGoalField.call_tag, GoalConditionOperator.less, "tag", 0, 0);
        ConditionalCallGoal goal = new ConditionalCallGoal(0, counterId, "test name",
                new Date(System.currentTimeMillis()), 0, List.of(condition), false, 0, GoalSource.user, false, null);

        exception.expect(ApiException.class);
        exception.expectMessage("call_tag не может иметь условие типа less");
        goalsService.create(counterId, goal);
    }

    @Test
    public void tryToCreateCallGoalConditionDurationInvalidOperator() {
        int counterId = createCounter();

        CallGoalCondition condition = new CallGoalCondition(CallGoalField.call_duration, GoalConditionOperator.contain, "10|30", 0, 0);
        ConditionalCallGoal goal = new ConditionalCallGoal(0, counterId, "test name",
                new Date(System.currentTimeMillis()), 0, List.of(condition), false, 0, GoalSource.user, false, null);

        exception.expect(ApiException.class);
        exception.expectMessage("call_duration не может иметь условие типа contain");
        goalsService.create(counterId, goal);
    }

    @Test
    public void tryToCreateCallGoalConditionDurationInvalidValue() {
        int counterId = createCounter();

        CallGoalCondition condition = new CallGoalCondition(CallGoalField.call_duration, GoalConditionOperator.between, "10-30", 0, 0);
        ConditionalCallGoal goal = new ConditionalCallGoal(0, counterId, "test name",
                new Date(System.currentTimeMillis()), 0, List.of(condition), false, 0, GoalSource.user, false, null);

        exception.expect(ApiException.class);
        exception.expectMessage("Значение для поля call_duration с оператором between должно иметь формат от|до");
        goalsService.create(counterId, goal);
    }

    @Test
    public void tryToCreateCallGoalConditionDurationInvalidValue2() {
        int counterId = createCounter();

        CallGoalCondition condition = new CallGoalCondition(CallGoalField.call_duration, GoalConditionOperator.between, "30|10", 0, 0);
        ConditionalCallGoal goal = new ConditionalCallGoal(0, counterId, "test name",
                new Date(System.currentTimeMillis()), 0, List.of(condition), false, 0, GoalSource.user, false, null);

        exception.expect(ApiException.class);
        exception.expectMessage("Значение для поля call_duration с оператором between должно иметь формат от|до");
        goalsService.create(counterId, goal);
    }

    @Test
    public void tryToCreateCallGoalConditionDurationInvalidValue3() {
        int counterId = createCounter();

        CallGoalCondition condition = new CallGoalCondition(CallGoalField.call_duration, GoalConditionOperator.greater, "10string", 0, 0);
        ConditionalCallGoal goal = new ConditionalCallGoal(0, counterId, "test name",
                new Date(System.currentTimeMillis()), 0, List.of(condition), false, 0, GoalSource.user, false, null);

        exception.expect(ApiException.class);
        exception.expectMessage("Значение для поля call_duration с оператором greater должно состоять только из цифр");
        goalsService.create(counterId, goal);
    }

    @Test
    public void createDefaultConditionalCallGoalWithFirstTimeCaller() {
        int counterId = createCounter();

        goalsService.createDefaultConditionalCallGoalsIfAbsent(counterId, true);

        List<DatabaseGoal> dbGoals = getGoalsByCounterId(counterId);

        Assert.assertEquals(3, dbGoals.size());
        Assert.assertEquals(
                Set.of(GoalStatus.Active),
                dbGoals.stream()
                        .map(DatabaseGoal::getStatus)
                        .collect(Collectors.toSet())
        );
        Assert.assertEquals(
                Set.of(GoalSource.auto),
                dbGoals.stream()
                        .map(DatabaseGoal::getGoalSource)
                        .collect(Collectors.toSet())
        );
        Assert.assertEquals(
                Set.of("Целевой звонок", "Уникально-целевой звонок", "Уникальный звонок"),
                dbGoals.stream()
                        .map(DatabaseGoal::getName)
                        .collect(Collectors.toSet())
        );
        for (DatabaseGoal g : dbGoals) {
            switch (g.getName()) {
                case "Целевой звонок" -> {
                    Assert.assertEquals(1, g.getConditions().size());
                    Assert.assertEquals(CallGoalField.call_duration.name(), g.getConditions().get(0).getField());
                    Assert.assertEquals(GoalConditionOperator.greater.name(), g.getConditions().get(0).getPatternType());
                    Assert.assertEquals("30", g.getConditions().get(0).getUrl());
                }
                case "Уникально-целевой звонок" -> {
                    Assert.assertEquals(2, g.getConditions().size());
                    Assert.assertEquals(
                            Set.of(CallGoalField.call_first.name(), CallGoalField.call_duration.name()),
                            g.getConditions().stream()
                                    .map(DatabaseGoalCondition::getField)
                                    .collect(Collectors.toSet())
                    );
                    Assert.assertEquals(
                            Set.of(GoalConditionOperator.exact.name(), GoalConditionOperator.greater.name()),
                            g.getConditions().stream()
                                    .map(DatabaseGoalCondition::getPatternType)
                                    .collect(Collectors.toSet())
                    );
                    Assert.assertEquals(
                            Set.of(Boolean.TRUE.toString(), "30"),
                            g.getConditions().stream()
                                    .map(DatabaseGoalCondition::getUrl)
                                    .collect(Collectors.toSet())
                    );
                }
                case "Уникальный звонок" -> {
                    Assert.assertEquals(1, g.getConditions().size());
                    Assert.assertEquals(CallGoalField.call_first.name(), g.getConditions().get(0).getField());
                    Assert.assertEquals(GoalConditionOperator.exact.name(), g.getConditions().get(0).getPatternType());
                    Assert.assertEquals(Boolean.TRUE.toString(), g.getConditions().get(0).getUrl());
                }
                default -> throw new IllegalArgumentException(g.getName() + " is an unknown goal");
            }
        }
    }

    @Test
    public void createDefaultConditionalCallGoalWithoutFirstTimeCaller() {
        int counterId = createCounter();

        goalsService.createDefaultConditionalCallGoalsIfAbsent(counterId, false);

        List<DatabaseGoal> dbGoals = getGoalsByCounterId(counterId);

        Assert.assertEquals(1, dbGoals.size());
        Assert.assertEquals(GoalStatus.Active, dbGoals.get(0).getStatus());
        Assert.assertEquals(GoalSource.auto, dbGoals.get(0).getGoalSource());
        Assert.assertEquals("Целевой звонок", dbGoals.get(0).getName());

        Assert.assertEquals(1, dbGoals.get(0).getConditions().size());
        Assert.assertEquals(CallGoalField.call_duration.name(), dbGoals.get(0).getConditions().get(0).getField());
        Assert.assertEquals(GoalConditionOperator.greater.name(), dbGoals.get(0).getConditions().get(0).getPatternType());
        Assert.assertEquals("30", dbGoals.get(0).getConditions().get(0).getUrl());
    }

    @Test
    public void createDefaultConditionalCallGoalWithOtherUserGoal() {
        int counterId = createCounter();

        var goal = new CallGoal(1, counterId, "test call goal " + counterId,
                new Date(System.currentTimeMillis()), 0, true,
                1, GoalSource.user, false, null);
        goalsService.create(counterId, goal);

        goalsService.createDefaultConditionalCallGoalsIfAbsent(counterId, false);

        List<DatabaseGoal> dbGoals = getGoalsByCounterId(counterId);

        Assert.assertEquals(2, dbGoals.size());
        Optional<DatabaseGoal> g = dbGoals.stream().filter(gl -> gl.getName().equals("Целевой звонок")).findFirst();
        Assert.assertTrue(g.isPresent());
        Assert.assertEquals(GoalStatus.Active, g.get().getStatus());
        Assert.assertEquals(GoalSource.auto, g.get().getGoalSource());
        Assert.assertEquals("Целевой звонок", g.get().getName());

        Assert.assertEquals(1, g.get().getConditions().size());
        Assert.assertEquals(CallGoalField.call_duration.name(), g.get().getConditions().get(0).getField());
        Assert.assertEquals(GoalConditionOperator.greater.name(), g.get().getConditions().get(0).getPatternType());
        Assert.assertEquals("30", g.get().getConditions().get(0).getUrl());
    }

    @Test
    public void createDefaultConditionalCallGoalWithOtherAutoGoal() {
        int counterId = createCounter();

        var goal = new CallGoal(1, counterId, "test call goal " + counterId,
                new Date(System.currentTimeMillis()), 0, true,
                1, GoalSource.auto, false, null);
        goalsService.create(counterId, goal);

        goalsService.createDefaultConditionalCallGoalsIfAbsent(counterId, false);

        List<DatabaseGoal> dbGoals = getGoalsByCounterId(counterId);

        Assert.assertEquals(2, dbGoals.size());
        Optional<DatabaseGoal> g = dbGoals.stream().filter(gl -> gl.getName().equals("Целевой звонок")).findFirst();
        Assert.assertTrue(g.isPresent());
        Assert.assertEquals(GoalStatus.Active, g.get().getStatus());
        Assert.assertEquals(GoalSource.auto, g.get().getGoalSource());
        Assert.assertEquals("Целевой звонок", g.get().getName());

        Assert.assertEquals(1, g.get().getConditions().size());
        Assert.assertEquals(CallGoalField.call_duration.name(), g.get().getConditions().get(0).getField());
        Assert.assertEquals(GoalConditionOperator.greater.name(), g.get().getConditions().get(0).getPatternType());
        Assert.assertEquals("30", g.get().getConditions().get(0).getUrl());
    }

    @Test
    public void createDefaultConditionalCallGoalWithUserConditionalCallGoal() {
        int counterId = createCounter();

        ConditionalCallGoal goal = new ConditionalCallGoal(
                0, counterId, "Цель: Звонок", new Date(System.currentTimeMillis()), 0, List.of(), false, 0,
                GoalSource.user, false, null
        );
        goalsService.create(counterId, goal);

        goalsService.createDefaultConditionalCallGoalsIfAbsent(counterId, false);

        List<DatabaseGoal> dbGoals = getGoalsByCounterId(counterId);

        Assert.assertEquals(2, dbGoals.size());
        Optional<DatabaseGoal> g = dbGoals.stream().filter(gl -> gl.getName().equals("Целевой звонок")).findFirst();
        Assert.assertTrue(g.isPresent());
        Assert.assertEquals(GoalStatus.Active, g.get().getStatus());
        Assert.assertEquals(GoalSource.auto, g.get().getGoalSource());
        Assert.assertEquals("Целевой звонок", g.get().getName());

        Assert.assertEquals(1, g.get().getConditions().size());
        Assert.assertEquals(CallGoalField.call_duration.name(), g.get().getConditions().get(0).getField());
        Assert.assertEquals(GoalConditionOperator.greater.name(), g.get().getConditions().get(0).getPatternType());
        Assert.assertEquals("30", g.get().getConditions().get(0).getUrl());
    }

    @Test
    public void notCreateDefaultConditionalCallGoalWithAutoConditionalCallGoal() {
        int counterId = createCounter();

        ConditionalCallGoal goal = new ConditionalCallGoal(
                0, counterId, "Цель: Звонок", new Date(System.currentTimeMillis()), 0, List.of(), false, 0,
                GoalSource.auto, false, null
        );
        goalsService.create(counterId, goal);

        goalsService.createDefaultConditionalCallGoalsIfAbsent(counterId, false);

        List<DatabaseGoal> dbGoals = getGoalsByCounterId(counterId);

        Assert.assertEquals(1, dbGoals.size());
        Assert.assertEquals(GoalStatus.Active, dbGoals.get(0).getStatus());
        Assert.assertEquals(GoalSource.auto, dbGoals.get(0).getGoalSource());
        Assert.assertEquals("Цель: Звонок", dbGoals.get(0).getName());
        Assert.assertEquals(GoalType.conditional_call, dbGoals.get(0).getType());
    }

    @Test
    public void notCreateDefaultConditionalCallGoalSecondTime() {
        int counterId = createCounter();

        goalsService.createDefaultConditionalCallGoalsIfAbsent(counterId, false);

        List<DatabaseGoal> dbGoals = getGoalsByCounterId(counterId);

        Assert.assertEquals(1, dbGoals.size());
        Assert.assertEquals(GoalStatus.Active, dbGoals.get(0).getStatus());
        Assert.assertEquals(GoalSource.auto, dbGoals.get(0).getGoalSource());
        Assert.assertEquals("Целевой звонок", dbGoals.get(0).getName());

        Assert.assertEquals(1, dbGoals.get(0).getConditions().size());
        Assert.assertEquals(CallGoalField.call_duration.name(), dbGoals.get(0).getConditions().get(0).getField());
        Assert.assertEquals(GoalConditionOperator.greater.name(), dbGoals.get(0).getConditions().get(0).getPatternType());
        Assert.assertEquals("30", dbGoals.get(0).getConditions().get(0).getUrl());

        goalsService.createDefaultConditionalCallGoalsIfAbsent(counterId, false);

        dbGoals = getGoalsByCounterId(counterId);

        Assert.assertEquals(1, dbGoals.size());
        Assert.assertEquals(GoalStatus.Active, dbGoals.get(0).getStatus());
        Assert.assertEquals(GoalSource.auto, dbGoals.get(0).getGoalSource());
        Assert.assertEquals("Целевой звонок", dbGoals.get(0).getName());

        Assert.assertEquals(1, dbGoals.get(0).getConditions().size());
        Assert.assertEquals(CallGoalField.call_duration.name(), dbGoals.get(0).getConditions().get(0).getField());
        Assert.assertEquals(GoalConditionOperator.greater.name(), dbGoals.get(0).getConditions().get(0).getPatternType());
        Assert.assertEquals("30", dbGoals.get(0).getConditions().get(0).getUrl());
    }

    @Test
    public void notCreateDefaultConditionalCallGoalAfterDeletion() {
        int counterId = createCounter();

        goalsService.createDefaultConditionalCallGoalsIfAbsent(counterId, false);

        List<DatabaseGoal> dbGoals = getGoalsByCounterId(counterId);

        Assert.assertEquals(1, dbGoals.size());
        Assert.assertEquals(GoalStatus.Active, dbGoals.get(0).getStatus());
        Assert.assertEquals(GoalSource.auto, dbGoals.get(0).getGoalSource());
        Assert.assertEquals("Целевой звонок", dbGoals.get(0).getName());

        Assert.assertEquals(1, dbGoals.get(0).getConditions().size());
        Assert.assertEquals(CallGoalField.call_duration.name(), dbGoals.get(0).getConditions().get(0).getField());
        Assert.assertEquals(GoalConditionOperator.greater.name(), dbGoals.get(0).getConditions().get(0).getPatternType());
        Assert.assertEquals("30", dbGoals.get(0).getConditions().get(0).getUrl());

        goalsService.deleteAll(counterId);

        goalsService.createDefaultConditionalCallGoalsIfAbsent(counterId, true);

        dbGoals = getGoalsByCounterId(counterId);

        Assert.assertEquals(1, dbGoals.size());
        Assert.assertEquals(GoalStatus.Deleted, dbGoals.get(0).getStatus());
        Assert.assertEquals(GoalSource.auto, dbGoals.get(0).getGoalSource());
        Assert.assertEquals("Целевой звонок", dbGoals.get(0).getName());
    }

    @Test
    public void createButtonGoalWithInvisibleSymbolsInConditions() {
        var counterId = createCounter();

        var originalPath = "?S1A\u0084\u0089";
        var buttonGoal = new ButtonGoal();
        buttonGoal.setName("button");
        buttonGoal.setCreateTime(new Date());
        buttonGoal.setGoalSource(GoalSource.user);
        buttonGoal.setCounterId(counterId);
        buttonGoal.setConditions(List.of(new GoalCondition(GoalConditionType.btn_path, originalPath, 0)));

        var goalE = goalsService.create(counterId, buttonGoal);
        var fromDb = goalsService.findById(counterId, goalE.getId());

        Assert.assertEquals(originalPath, ((ButtonGoal) fromDb).getConditions().get(0).getValue());
    }

    @Test
    public void dontAllowToDeleteStepOfCompositeGoal() {
        var counterId = createCounter();

        var urlGoal = new UrlGoal();
        urlGoal.setName("url step");
        urlGoal.setCreateTime(new Date());
        urlGoal.setGoalSource(GoalSource.user);
        urlGoal.setCounterId(counterId);
        urlGoal.setConditions(List.of(new GoalCondition(GoalConditionType.exact, "ya.ru", 0)));

        var compositeGoal = new CompositeGoal();
        compositeGoal.setName("composite");
        compositeGoal.setCreateTime(new Date());
        compositeGoal.setGoalSource(GoalSource.user);
        compositeGoal.setCounterId(counterId);
        compositeGoal.setSteps(List.of(urlGoal));

        var goalE = goalsService.create(counterId, compositeGoal);
        var stepGoalId = ((CompositeGoal) goalE).getSteps().get(0).getId();

        exception.expect(ApiException.class);
        goalsService.delete(counterId, stepGoalId);
    }

    @Test
    public void allowToDeleteCompositeGoal() {
        var counterId = createCounter();

        var urlGoal = new UrlGoal();
        urlGoal.setName("url step");
        urlGoal.setCreateTime(new Date());
        urlGoal.setGoalSource(GoalSource.user);
        urlGoal.setCounterId(counterId);
        urlGoal.setConditions(List.of(new GoalCondition(GoalConditionType.exact, "ya.ru", 0)));

        var compositeGoal = new CompositeGoal();
        compositeGoal.setName("composite");
        compositeGoal.setCreateTime(new Date());
        compositeGoal.setGoalSource(GoalSource.user);
        compositeGoal.setCounterId(counterId);
        compositeGoal.setSteps(List.of(urlGoal));

        var goalE = goalsService.create(counterId, compositeGoal);
        var compositeGoalId = goalE.getId();

        goalsService.delete(counterId, compositeGoalId);

        Assert.assertThat(
                goalsService.findByCounterId(counterId, true).stream().filter(goal -> goal.getId() == compositeGoalId).findAny(),
                MoreMatchers.isPresent()
        );

        Assert.assertThat(
                goalsService.findByCounterId(counterId, false).stream().filter(goal -> goal.getId() == compositeGoalId).findAny(),
                MoreMatchers.isEmpty()
        );

    }

    @Test
    public void createFavoriteGoal() {
        var counterId = createCounter();

        var offlineGoal = new OfflineGoal();
        offlineGoal.setName("Create favorite goal");
        offlineGoal.setCounterId(counterId);
        offlineGoal.setIsFavorite(true);

        var goal = goalsService.create(counterId, offlineGoal);

        DatabaseGoal dbGoal = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());
        Assert.assertEquals(goal.getId(), dbGoal.getGoalId());
        Assert.assertEquals(counterId, dbGoal.getCounterId());
        Assert.assertEquals("Create favorite goal", dbGoal.getName());
        Assert.assertTrue(dbGoal.isFavorite());
    }

    @Test
    public void updateToFavoriteGoal() {
        var counterId = createCounter();

        var offlineGoal = new OfflineGoal();
        offlineGoal.setName("Update to favorite goal");
        offlineGoal.setCounterId(counterId);
        offlineGoal.setIsFavorite(false);

        var goal = goalsService.create(counterId, offlineGoal);

        DatabaseGoal beforeUpdate = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());
        Assert.assertEquals(goal.getId(), beforeUpdate.getGoalId());
        Assert.assertEquals(counterId, beforeUpdate.getCounterId());
        Assert.assertEquals("Update to favorite goal", beforeUpdate.getName());
        Assert.assertFalse(beforeUpdate.isFavorite());

        goal.setIsFavorite(true);
        goalsService.update(counterId, goal.getId(), goal);

        DatabaseGoal afterUpdate = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());
        Assert.assertEquals(goal.getId(), afterUpdate.getGoalId());
        Assert.assertEquals(counterId, afterUpdate.getCounterId());
        Assert.assertEquals("Update to favorite goal", afterUpdate.getName());
        Assert.assertTrue(afterUpdate.isFavorite());
    }

    @Test
    public void updateFromFavoriteGoal() {
        var counterId = createCounter();

        var offlineGoal = new OfflineGoal();
        offlineGoal.setName("Update from favorite goal");
        offlineGoal.setCounterId(counterId);
        offlineGoal.setIsFavorite(true);

        var goal = goalsService.create(counterId, offlineGoal);

        DatabaseGoal beforeUpdate = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());
        Assert.assertEquals(goal.getId(), beforeUpdate.getGoalId());
        Assert.assertEquals(counterId, beforeUpdate.getCounterId());
        Assert.assertEquals("Update from favorite goal", beforeUpdate.getName());
        Assert.assertTrue(beforeUpdate.isFavorite());

        goal.setIsFavorite(false);
        goalsService.update(counterId, goal.getId(), goal);

        DatabaseGoal afterUpdate = getGoalByGoalIdQuery(goal.getCounterId(), goal.getId());
        Assert.assertEquals(goal.getId(), afterUpdate.getGoalId());
        Assert.assertEquals(counterId, afterUpdate.getCounterId());
        Assert.assertEquals("Update from favorite goal", afterUpdate.getName());
        Assert.assertFalse(afterUpdate.isFavorite());
    }

    @Test
    public void getCreatedFavoriteGoalsSorted() {
        var counterId = createCounter();

        var firstNonFavGoal = new ActionGoal();
        firstNonFavGoal.setName("First non favorite goal");
        firstNonFavGoal.setCounterId(counterId);
        firstNonFavGoal.setConditions(List.of(new GoalCondition(GoalConditionType.exact, "ya.ru", 0)));
        firstNonFavGoal.setIsFavorite(false);

        var firstFavGoal = new ActionGoal();
        firstFavGoal.setName("First favorite goal");
        firstFavGoal.setCounterId(counterId);
        firstFavGoal.setConditions(List.of(new GoalCondition(GoalConditionType.exact, "ya.ru", 0)));
        firstFavGoal.setIsFavorite(true);

        var secondNonFavGoal = new ActionGoal();
        secondNonFavGoal.setName("Second non favorite goal");
        secondNonFavGoal.setCounterId(counterId);
        secondNonFavGoal.setConditions(List.of(new GoalCondition(GoalConditionType.exact, "ya.ru", 0)));
        secondNonFavGoal.setIsFavorite(false);

        var secondFavGoal = new ActionGoal();
        secondFavGoal.setName("Second favorite goal");
        secondFavGoal.setCounterId(counterId);
        secondFavGoal.setConditions(List.of(new GoalCondition(GoalConditionType.exact, "ya.ru", 0)));
        secondFavGoal.setIsFavorite(true);

        List<GoalE> goalList = new ArrayList<>();
        goalList.add(firstNonFavGoal);
        goalList.add(firstFavGoal);
        goalList.add(secondNonFavGoal);
        goalList.add(secondFavGoal);

        List<GoalE> addedGoals = new ArrayList<>();
        for (GoalE goal : goalList) {
            addedGoals.add(goalsService.create(counterId, goal));
        }
        List<GoalE> byCounterId = goalsService.findByCounterId(counterId);
        int[] expectedPermutation = {1, 3, 0, 2};
        for (int i = 0; i < expectedPermutation.length; i++) {
            int perm = expectedPermutation[i];
            Assert.assertEquals(counterId, byCounterId.get(i).getCounterId());
            Assert.assertEquals(addedGoals.get(perm).getName(), byCounterId.get(i).getName());
            Assert.assertEquals(addedGoals.get(perm).getIsFavorite(), byCounterId.get(i).getIsFavorite());
            Assert.assertEquals(addedGoals.get(perm).getId(), byCounterId.get(i).getId());
        }
    }

    @Test
    public void getUpdatedFavoriteGoalsSorted() {
        var counterId = createCounter();

        var firstNonFavGoal = new ActionGoal();
        firstNonFavGoal.setName("Updated to favorite goal");
        firstNonFavGoal.setCounterId(counterId);
        firstNonFavGoal.setConditions(List.of(new GoalCondition(GoalConditionType.exact, "ya.ru", 0)));
        firstNonFavGoal.setIsFavorite(false);

        var firstFavGoal = new ActionGoal();
        firstFavGoal.setName("Favorite goal");
        firstFavGoal.setCounterId(counterId);
        firstFavGoal.setConditions(List.of(new GoalCondition(GoalConditionType.exact, "ya.ru", 0)));
        firstFavGoal.setIsFavorite(true);

        var secondNonFavGoal = new ActionGoal();
        secondNonFavGoal.setName("Non favorite goal");
        secondNonFavGoal.setCounterId(counterId);
        secondNonFavGoal.setConditions(List.of(new GoalCondition(GoalConditionType.exact, "ya.ru", 0)));
        secondNonFavGoal.setIsFavorite(false);

        var secondFavGoal = new ActionGoal();
        secondFavGoal.setName("Updated from favorite goal");
        secondFavGoal.setCounterId(counterId);
        secondFavGoal.setConditions(List.of(new GoalCondition(GoalConditionType.exact, "ya.ru", 0)));
        secondFavGoal.setIsFavorite(true);

        List<GoalE> goalList = new ArrayList<>();
        goalList.add(firstNonFavGoal);
        goalList.add(firstFavGoal);
        goalList.add(secondNonFavGoal);
        goalList.add(secondFavGoal);

        List<GoalE> addedGoals = new ArrayList<>();
        for (GoalE goal : goalList) {
            addedGoals.add(goalsService.create(counterId, goal));
        }
        List<GoalE> byCounterId = goalsService.findByCounterId(counterId);
        int[] expectedPermutation = {1, 3, 0, 2};
        for (int i = 0; i < expectedPermutation.length; i++) {
            int perm = expectedPermutation[i];
            Assert.assertEquals(counterId, byCounterId.get(i).getCounterId());
            Assert.assertEquals(addedGoals.get(perm).getName(), byCounterId.get(i).getName());
            Assert.assertEquals(addedGoals.get(perm).getIsFavorite(), byCounterId.get(i).getIsFavorite());
            Assert.assertEquals(addedGoals.get(perm).getId(), byCounterId.get(i).getId());
        }

        addedGoals.get(0).setIsFavorite(true);
        goalsService.update(counterId, addedGoals.get(0).getId(), addedGoals.get(0));

        addedGoals.get(3).setIsFavorite(false);
        goalsService.update(counterId, addedGoals.get(3).getId(), addedGoals.get(3));

        List<GoalE> updatedByCounterId = goalsService.findByCounterId(counterId);
        expectedPermutation = new int[]{0, 1, 2, 3};
        for (int i = 0; i < expectedPermutation.length; i++) {
            int perm = expectedPermutation[i];
            Assert.assertEquals(counterId, updatedByCounterId.get(i).getCounterId());
            Assert.assertEquals(addedGoals.get(perm).getName(), updatedByCounterId.get(i).getName());
            Assert.assertEquals(addedGoals.get(perm).getIsFavorite(), updatedByCounterId.get(i).getIsFavorite());
            Assert.assertEquals(addedGoals.get(perm).getId(), updatedByCounterId.get(i).getId());
        }
    }

    @Test
    public void tryAddCompositeGoalWithFavoriteStep() {
        var counterId = createCounter();

        var urlGoal = new UrlGoal();
        urlGoal.setName("Favorite step goal");
        urlGoal.setCounterId(counterId);
        urlGoal.setConditions(List.of(new GoalCondition(GoalConditionType.exact, "ya.ru", 0)));
        urlGoal.setIsFavorite(true);

        var compositeGoal = new CompositeGoal();
        compositeGoal.setName("Composite goal");
        compositeGoal.setCounterId(counterId);
        compositeGoal.setSteps(List.of(urlGoal));

        exception.expect(ApiException.class);
        exception.expectMessage("Шаг составной цели нельзя добавить в избранные цели");
        goalsService.create(counterId, compositeGoal);
    }

    private PhoneGoal createPhoneGoal(Integer counterId) {
        var goal = new PhoneGoal();
        goal.setCreateTime(new Date());
        goal.setGoalSource(GoalSource.user);
        goal.setCounterId(counterId);
        var condition = new GoalCondition();
        condition.setOperator(GoalConditionType.exact);
        String randomPhone = "+" + (79000000000L + new Random().nextInt(1000000000));
        condition.setValue(randomPhone);
        goal.setConditions(List.of(condition));
        goal.setName(randomPhone);
        return goal;
    }

    private OfflineGoal createOfflineGoal(Integer counterId) {
        var goal = new OfflineGoal();
        goal.setCreateTime(new Date());
        goal.setGoalSource(GoalSource.user);
        goal.setCounterId(counterId);
        goal.setName("some");
        return goal;
    }

    private Set<String> getHiddenPhonesAsSet(int counterId) {
        return getHiddenPhonesAsMap(counterId).keySet();
    }

    private Map<String, Integer> getHiddenPhonesAsMap(int counterId) {
        Map<String, Integer> result = new HashMap<>();

        convMainTemplate.query(
                "select hidden_phones from counter_options where counter_id = ?",
                rs -> {
                    String[] phones = StringUtils.split(rs.getString("hidden_phones"), HIDDEN_PHONES_SEPARATOR);
                    if (phones != null) {
                        for (String phone : phones) {
                            result.computeIfAbsent(phone, k -> 0);
                            result.computeIfPresent(phone, (k, v) -> v + 1);
                        }
                    }
                },
                counterId
        );
        return result;
    }

    private void deleteGoal(int counterId, long goalId) {
        convMainTemplate.update(
                "UPDATE ad_goals SET `status` = ? WHERE counter_id = ? AND goal_id = ?",
                GoalStatus.Deleted.toString(),
                counterId,
                goalId
        );
    }

    private DatabaseGoal getGoalByGoalIdQuery(Integer counterId, Long goalId) {
        return convMainTemplate.queryForObject(
                "SELECT * " +
                        "FROM ad_goals " +
                        "WHERE counter_id = ? AND goal_id = ?",
                GoalsService.GoalRowMapper,
                counterId,
                goalId
        );
    }

    private List<DatabaseGoal> getGoalsByCounterId(int counterId) {
        Map<Integer, DatabaseGoal> map = new HashMap<>();

        convMainTemplate.query(
                "select ag.* from ad_goals as ag " +
                        "where ag.counter_id = ? ",
                rs -> {
                    map.put(
                            rs.getInt("goal_id"),
                            new DatabaseGoal(
                                    rs.getInt("goal_id"),
                                    rs.getInt("counter_id"),
                                    rs.getInt("serial"),
                                    rs.getString("name"),
                                    rs.getLong("depth"),
                                    GoalType.valueOf(rs.getString("goal_type")),
                                    GoalStatus.valueOf(rs.getString("status")),
                                    rs.getTimestamp("create_time"),
                                    rs.getDouble("default_price"),
                                    rs.getString("goal_flag"),
                                    rs.getInt("prev_goal_id"),
                                    rs.getInt("parent_goal_id"),
                                    rs.getBoolean("direct_retargeting"),
                                    GoalSource.valueOf(rs.getString("source")),
                                    rs.getBoolean("hide_phone_number"),
                                    rs.getBoolean("is_favorite"),
                                    rs.getInt("partner_goal_id")
                            )
                    );
                },
                counterId
        );

        convMainTemplate.query(
                "select * from ad_goals_urls where goal_id in (" + F.join(map.keySet(), ", ") + ")",
                rs -> {
                    DatabaseGoal dg = map.get(rs.getInt("goal_id"));
                    dg.getConditions().add(
                            new DatabaseGoalCondition(
                                    rs.getInt("goal_id"),
                                    rs.getInt("serial"),
                                    rs.getString("field"),
                                    rs.getString("pattern_type"),
                                    rs.getString("url")
                            )
                    );
                }
        );

        return new ArrayList<>(map.values());
    }

    private Boolean isButtonGoalExist(Integer counterId) {
        List<Integer> alreadyEnabled = convMainTemplate.queryForList(
                "SELECT counter_id FROM counter_options WHERE counter_id = ? && button_goals = 1",
                Integer.class,
                counterId
        );

        return alreadyEnabled.contains(counterId);
    }

    private List<DatabaseGoalCondition> getGoalConditionsQuery(Long goalId) {
        return convMainTemplate.query(
                "SELECT goal_id, serial, field, pattern_type, url " +
                        "FROM ad_goals_urls " +
                        "WHERE goal_id = ? " +
                        "ORDER BY `serial`",
                (rs, rowNum) -> {
                    int serial = rs.getInt("serial");
                    String goalConditionType = rs.getString("pattern_type");
                    String url = rs.getString("url");
                    String field = rs.getString("field");
                    return new DatabaseGoalCondition(goalId, serial, field, goalConditionType, url);
                },
                goalId
        );
    }

    private int createCounter() {
        return (int) convMainTemplate.updateRowGetGeneratedKey(
                "INSERT INTO counters " +
                        "(`name`," +
                        "create_time," +
                        "external_class," +
                        "external_cid," +
                        "email," +
                        "LayerID," +
                        "informer_color," +
                        "informer_indicators) " +
                        "VALUES (?,NOW(),?,?,?,?,?,?)",
                "test",
                0,
                0,
                "test email",
                1,
                "test informer color",
                "test informer indicators"
        );
    }

    private static String clipLeadingPlus(String str) {
        if (str == null || str.isEmpty()) return str;
        return str.startsWith("+") ? str.substring(1) : str;
    }

    @Configuration
    @Import({JdbcTemplateConfig.class, ApiValidatorConfig.class, LocaleDictionariesConfig.class, MessengerValidatorConfig.class, SocialNetworkValidatorConfig.class, CounterOptionsServiceConfig.class})
    public static class Config {

        @Bean
        public GoalsService goalsService(MySqlJdbcTemplate convMainTemplate, ApiInputValidator validator,
                                         LocaleDictionaries dictionaries, CounterOptionsService counterOptionsService) {
            GoalsService goalsService = new GoalsService();
            goalsService.setJdbcTemplate(convMainTemplate);
            goalsService.setValidator(validator);
            goalsService.setCounterLimitsService(counterOptionsService);
            goalsService.setFormGoalsService(counterOptionsService);
            goalsService.setButtonGoalsService(counterOptionsService);
            goalsService.setDictionaries(dictionaries);
            goalsService.setConditionalCallGoalEnabled(true);

            PropertyUtilsMysql propertyUtils = new PropertyUtilsMysql();
            propertyUtils.setPropertiesDb(convMainTemplate);
            propertyUtils.afterPropertiesSet();

            GoalIdGenerationService goalIdGenerationService = new GoalIdGenerationService();
            goalIdGenerationService.setConvMain(convMainTemplate);

            goalsService.setGoalIdGenerationService(goalIdGenerationService);
            return goalsService;
        }
    }
}
