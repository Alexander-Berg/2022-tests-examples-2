package ru.yandex.metrika.metr19370;

import java.util.List;

import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.dbclients.mysql.RowMappers;
import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;

/**
 * Created by orantius on 12/10/15.
 */
public class GoalsFix {
    public static void main(String[] args) {
        MySqlJdbcTemplate convMain = AllDatabases.getTemplate("localhost", 3311, "metrica", XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_old"), "conv_main");
        List<Integer> parentGoals = convMain.query("SELECT parent_goal_id " +
                "FROM ad_goals WHERE prev_goal_id = 0 AND parent_goal_id > 0 AND STATUS = 'Active' " +
                "GROUP BY parent_goal_id HAVING COUNT(*) > 1 ", RowMappers.INTEGER);
        System.out.println("parentGoals = " + parentGoals.size());
        int updated = 0;
        for (Integer parentGoal : parentGoals) {
            List<Integer> stepIds = convMain.query("SELECT goal_id FROM ad_goals " +
                    "WHERE parent_goal_id = ? ORDER BY SERIAL;", RowMappers.INTEGER, parentGoal);
            int prevStepId = 0;
            for (Integer stepId : stepIds) {
                updated += convMain.update("update ad_goals set prev_goal_id = ? where goal_id = ?", prevStepId, stepId);
                prevStepId = stepId;
            }
        }
        System.out.println("updated = " + updated);
    }
}
// 9 35
