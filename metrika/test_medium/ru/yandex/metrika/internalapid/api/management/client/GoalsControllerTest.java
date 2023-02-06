package ru.yandex.metrika.internalapid.api.management.client;

import java.util.Arrays;
import java.util.Collections;
import java.util.Date;
import java.util.List;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import org.springframework.test.context.web.WebAppConfiguration;
import org.springframework.test.web.servlet.MvcResult;

import ru.yandex.metrika.api.management.client.external.goals.ButtonGoal;
import ru.yandex.metrika.api.management.client.external.goals.GoalCondition;
import ru.yandex.metrika.api.management.client.external.goals.GoalConditionType;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.goals.GoalMarketType;
import ru.yandex.metrika.api.management.client.external.goals.GoalSource;
import ru.yandex.metrika.api.management.client.external.goals.SiteSearchGoal;
import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.internalapid.api.config.GoalsControllerConfiguration;
import ru.yandex.metrika.internalapid.common.validators.SubscribedCounterGoalValidator;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.wrappers.GoalWrapper;

import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.notNullValue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.asyncDispatch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@RunWith(SpringJUnit4ClassRunner.class)
@WebAppConfiguration
@ContextConfiguration(classes = {GoalsControllerConfiguration.class})
public class GoalsControllerTest extends BaseIntapiTest {
    public static final String URI = "/subscription/goals/v1/counter/{counterId}";
    public static final Integer COUNTER_ID = 67356880;
    public static final Integer NOT_SUBSCRIBED_COUNTER_ID = 20;
    public static final Integer SUBSCRIBED_COUNTER_WITH_AUTOGOALS_DISABLED_ID = 100;
    public static final Integer NON_EXISTENT_COUNTER_ID = 1;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Autowired
    private SubscribedCounterGoalValidator subscribedCounterGoalValidator;

    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
    }

    @Before
    public void setup() {
        mockMvcBaseSetup();
        initData();
    }

    public void initData() {
        createCounter(COUNTER_ID, 24);
        makeAutogoalsEnabled(COUNTER_ID);
        createCounter(SUBSCRIBED_COUNTER_WITH_AUTOGOALS_DISABLED_ID, 24);
        createCounter(NOT_SUBSCRIBED_COUNTER_ID, 24);
        initSubscribedCounters();
    }

    @Test
    public void addGoal() throws Exception {
        MvcResult result = mockMvc.perform(
                post(URI, COUNTER_ID)
                        .accept(MediaType.APPLICATION_JSON_VALUE)
                        .contentType(MediaType.APPLICATION_JSON_VALUE)
                        .queryParam("slug", "CALL_BACK")
                        .content(objectMapper.writeValueAsString(buttonGoal(null, null, buttonGoalConditions())))
        ).andDo(print()) //.andExpect(request().asyncStarted())
                .andReturn();

        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isOk())
                .andExpect(jsonPath("goal.id", notNullValue()))
                .andExpect(jsonPath("goal.name", is("Автоцель: обратный звонок")))
                .andExpect(jsonPath("goal.type", is("button")))
                .andExpect(jsonPath("goal.defaultPrice", is(0.0)))
                .andExpect(jsonPath("goal.goalSource", is("auto")))
                .andExpect(jsonPath("goal.conditions[0].type", is("btn_path")))
                .andExpect(jsonPath("goal.conditions[0].url", is("test")));
    }

    @Test
    public void tryToAddGoalWithWrongSLUG() throws Exception {
        MvcResult result = mockMvc.perform(
                post(URI, COUNTER_ID)
                        .accept(MediaType.APPLICATION_JSON_VALUE)
                        .contentType(MediaType.APPLICATION_JSON_VALUE)
                        .queryParam("slug", "test")
                        .content(objectMapper.writeValueAsString(buttonGoal("", null, buttonGoalConditions())))
        ).andDo(print()) //.andExpect(request().asyncStarted())
                .andReturn();
        result.getAsyncResult();

        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errors[0].message", is("Невалидный SLUG 'test'")));
    }

    @Test
    public void tryToAddGoalToNotSubscribedCounter() throws Exception {
        MvcResult result = mockMvc.perform(
                post(URI, NOT_SUBSCRIBED_COUNTER_ID)
                        .accept(MediaType.APPLICATION_JSON_VALUE)
                        .contentType(MediaType.APPLICATION_JSON_VALUE)
                        .queryParam("slug", "CALL_BACK")
                        .content(objectMapper.writeValueAsString(buttonGoal("", null, buttonGoalConditions())))
        ).andDo(print()) //.andExpect(request().asyncStarted())
                .andReturn();
        result.getAsyncResult();

        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errors[0].message", is("Cчетчик 20 не подключен к подписке")));
    }

    @Test
    public void tryToAddGoalToSubscribedCounterButWithDisabledAutogoalsFlag() throws Exception {
        MvcResult result = mockMvc.perform(
                post(URI, SUBSCRIBED_COUNTER_WITH_AUTOGOALS_DISABLED_ID)
                        .accept(MediaType.APPLICATION_JSON_VALUE)
                        .contentType(MediaType.APPLICATION_JSON_VALUE)
                        .queryParam("slug", "CALL_BACK")
                        .content(objectMapper.writeValueAsString(buttonGoal("", null, buttonGoalConditions())))
        ).andDo(print()) //.andExpect(request().asyncStarted())
                .andReturn();
        result.getAsyncResult();

        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errors[0].message", is("Не включена опция \"Автоматические цели\" у счетчика 100")));
    }

    @Test
    public void tryToAddGoalWithExistentName() throws Exception {
        MvcResult result = mockMvc.perform(
                post(URI, COUNTER_ID)
                        .accept(MediaType.APPLICATION_JSON_VALUE)
                        .contentType(MediaType.APPLICATION_JSON_VALUE)
                        .queryParam("slug", "CALL_BACK")
                        .content(objectMapper.writeValueAsString(buttonGoal("test", null, buttonGoalConditions())))
        ).andDo(print()) //.andExpect(request().asyncStarted())
                .andReturn();
        result.getAsyncResult();

        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errors[0].message", is("У цели название должно быть пустым")));
    }

    @Test
    public void tryToAddGoalWithExistentDefaultPrice() throws Exception {
        MvcResult result = mockMvc.perform(
                post(URI, COUNTER_ID)
                        .accept(MediaType.APPLICATION_JSON_VALUE)
                        .contentType(MediaType.APPLICATION_JSON_VALUE)
                        .queryParam("slug", "CALL_BACK")
                        .content(objectMapper.writeValueAsString(buttonGoal(null, 100.0, buttonGoalConditions())))
        ).andDo(print()) //.andExpect(request().asyncStarted())
                .andReturn();
        result.getAsyncResult();

        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errors[0].message", is("У цели поле default_price должно быть пустым")));
    }

    @Test
    public void tryToAddGoalWithWrongGoalType() throws Exception {
        MvcResult result = mockMvc.perform(
                post(URI, COUNTER_ID)
                        .accept(MediaType.APPLICATION_JSON_VALUE)
                        .contentType(MediaType.APPLICATION_JSON_VALUE)
                        .queryParam("slug", "CALL_BACK")
                        .content(objectMapper.writeValueAsString(siteSearchGoal()))
        ).andDo(print()) //.andExpect(request().asyncStarted())
                .andReturn();
        result.getAsyncResult();

        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errors[0].message", is("Невалидный тип цели search. Тип цели должно быть button")));
    }

    @Test
    public void tryToAddGoalWithNoGoalConditions() throws Exception {
        MvcResult result = mockMvc.perform(
                post(URI, COUNTER_ID)
                        .accept(MediaType.APPLICATION_JSON_VALUE)
                        .contentType(MediaType.APPLICATION_JSON_VALUE)
                        .queryParam("slug", "CALL_BACK")
                        .content(objectMapper.writeValueAsString(buttonGoal(null, null, Collections.emptyList())))
        ).andDo(print()) //.andExpect(request().asyncStarted())
                .andReturn();
        result.getAsyncResult();

        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errors[0].message", is("Цель \"Клик по кнопке\" должна иметь хотя бы одно условие достижения")));
    }

    @Test
    public void tryToAddGoalWithWrongGoalConditions() throws Exception {
        MvcResult result = mockMvc.perform(
                post(URI, COUNTER_ID)
                        .accept(MediaType.APPLICATION_JSON_VALUE)
                        .contentType(MediaType.APPLICATION_JSON_VALUE)
                        .queryParam("slug", "CALL_BACK")
                        .content(objectMapper.writeValueAsString(buttonGoal(null, null, searchGoalConditions())))
        ).andDo(print()) //.andExpect(request().asyncStarted())
                .andReturn();
        result.getAsyncResult();

        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errors[0].message", is("Цель button не может иметь условие типа search")));
    }

    @Test
    public void tryToAddGoalToDeletedCounter() throws Exception {
        mockMvc.perform(
                post(URI, NON_EXISTENT_COUNTER_ID)
                    .accept(MediaType.APPLICATION_JSON_VALUE)
                    .contentType(MediaType.APPLICATION_JSON_VALUE)
                    .queryParam("slug", "CALL_BACK")
                    .content(objectMapper.writeValueAsString(buttonGoal(null, 100.0, buttonGoalConditions())))
                )
        .andExpect(status().isNotFound())
        .andExpect(jsonPath("$.errors[0].message", is("Entity not found")));
    }

    private void makeAutogoalsEnabled(int counterId) {
        convMain.update(
                "INSERT INTO counter_options " +
                        "(counter_id," +
                        "autogoals_enabled) " +
                        "VALUES (?,?) " +
                        "ON DUPLICATE KEY UPDATE " +
                        "autogoals_enabled = VALUES(autogoals_enabled);",
                counterId,
                true
        );
    }

    private void initSubscribedCounters() {
        List<Integer> subscribedCounterIds = List.of(COUNTER_ID, SUBSCRIBED_COUNTER_WITH_AUTOGOALS_DISABLED_ID);
        dicts.batchInsert(
                "INSERT IGNORE INTO subscribed_counters (counter_id)",
                F.map(subscribedCounterIds, Arrays::asList)
        );

        subscribedCounterGoalValidator.reloadSubscribedCounters();
    }

    private List<GoalCondition> buttonGoalConditions() {
        return Arrays.asList(
                new GoalCondition(GoalConditionType.btn_path, "test", 0)
        );
    }

    private List<GoalCondition> searchGoalConditions() {
        return Arrays.asList(
                new GoalCondition(GoalConditionType.search, "test", 0)
        );
    }

    private GoalWrapper buttonGoal(String name, Double defaultPrice, List<GoalCondition> goalConditions) {
        GoalE goal = new ButtonGoal(
                0, 0, name, new Date(System.currentTimeMillis()),
                defaultPrice, GoalMarketType.empty, goalConditions,
                false, 0, 0, GoalSource.auto, false, null);

        return new GoalWrapper(goal);
    }

    private GoalWrapper siteSearchGoal() {
        GoalE goal = new SiteSearchGoal(
                0, 0, null, new Date(System.currentTimeMillis()),
                null, GoalMarketType.empty, searchGoalConditions(),
                false, 0, 0, GoalSource.auto, false, null);

        return new GoalWrapper(goal);
    }
}
