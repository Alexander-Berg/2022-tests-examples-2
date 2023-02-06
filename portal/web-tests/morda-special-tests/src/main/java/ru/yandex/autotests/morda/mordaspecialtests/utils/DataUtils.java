package ru.yandex.autotests.morda.mordaspecialtests.utils;

import org.hamcrest.Matcher;
import ru.yandex.autotests.morda.mordaspecialtests.data.ProjectInfo;
import ru.yandex.testlab.wiki.Wiki;

import java.util.List;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.flatten;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.select;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24/10/14
 */
public class DataUtils {
    public static List<ProjectInfo.ProjectInfoCase> getData(boolean rc) {
        Matcher<ProjectInfo> matcher;

        if (rc) {
            matcher = having(on(ProjectInfo.class).getTest(), not(isEmptyOrNullString()));
        } else {
            matcher = allOf(
                    having(on(ProjectInfo.class).isInProd(), is(true)),
                    having(on(ProjectInfo.class).getTest(), not(isEmptyOrNullString())),
                    having(on(ProjectInfo.class).getProd(), not(isEmptyOrNullString()))
            );
        }

        return flatten(
                extract(
                        select(
                                Wiki.getInstance().populate(ProjectInfo.class),
                                matcher
                        ),
                        on(ProjectInfo.class).getProjectInfoCases()
                )
        );
    }
}
