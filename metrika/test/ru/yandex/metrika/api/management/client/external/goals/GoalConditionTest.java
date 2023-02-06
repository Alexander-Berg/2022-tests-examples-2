package ru.yandex.metrika.api.management.client.external.goals;

import java.sql.SQLException;

import com.google.common.base.Throwables;
import org.apache.commons.lang3.mutable.MutableInt;
import org.junit.Ignore;

import ru.yandex.metrika.api.management.client.GoalsTransformer;
import ru.yandex.metrika.api.management.client.model.DatabaseGoalCondition;
import ru.yandex.metrika.dbclients.mysql.IterableResultSet;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;

import static ru.yandex.metrika.tool.AllDatabases.getTemplate;

/**
 * Created by orantius on 04.06.17.
 */
@Ignore
public class GoalConditionTest {
    public static void main(String[] args) {

        MySqlJdbcTemplate template = getTemplate("localhost", 3311, "metrika", XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_old"), "conv_main");
        MutableInt coutn = new MutableInt();
        GoalConditionValidator v = new GoalConditionValidator();
        IterableResultSet<Object> objects = template.queryStreaming(
                "select " +
                        "agu.*, " +
                        "ag.goal_type " +
                        "from ad_goals_urls as agu " +
                        "inner join ad_goals as ag using(goal_id) ",
                (rs, i) -> {
                    try {
                        long goalId = rs.getLong("goal_id");
                        int serial = rs.getInt("serial");
                        String field = rs.getString("field");
                        String patternType = rs.getString("pattern_type");
                        String url = rs.getString("url");

                        DatabaseGoalCondition c = new DatabaseGoalCondition(
                                goalId,
                                serial,
                                field,
                                patternType,
                                url
                        );

                        GoalType goalType = GoalType.valueOf(rs.getString("goal_type"));

                        boolean valid = v.isValid((GoalCondition) GoalsTransformer.conditionByGoalType(goalType, c), null);
                        if (!valid) {
                            System.out.println("c = " + c);
                            coutn.increment();
                        }
                    } catch (SQLException e) {
                        Throwables.propagate(e);
                    }
                    return null;
                }
        );
    }
}
