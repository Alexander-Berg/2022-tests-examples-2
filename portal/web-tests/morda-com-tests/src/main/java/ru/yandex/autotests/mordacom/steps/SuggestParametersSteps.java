package ru.yandex.autotests.mordacom.steps;

import org.hamcrest.MatcherAssert;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.Map;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 16.12.2014.
 */
public class SuggestParametersSteps {
    @Step
    public void containsParameter(Map<String,String> suggestParameters, String parameter) {
        MatcherAssert.assertThat("Параметр " + parameter + " не найден", suggestParameters.containsKey(parameter));
    }

    @Step
    public void parameterHasCorrectValue(Map<String,String> suggestParameters, String parameter, String value) {
        MatcherAssert.assertThat("Неверное значение параметра " + parameter, suggestParameters.get(parameter).equals(value));
    }
}
