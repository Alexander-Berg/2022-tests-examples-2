package ru.yandex.autotests.morda.restassured.requests;

import ru.yandex.qatools.allure.Allure;
import ru.yandex.qatools.allure.events.StepFailureEvent;
import ru.yandex.qatools.allure.events.StepFinishedEvent;
import ru.yandex.qatools.allure.events.StepStartedEvent;

import java.util.function.Supplier;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 12/05/16
 */
public class RequestHelpers {
    public static <K> K wrapStep(String stepName, Supplier<K> supplier) {
        Allure.LIFECYCLE.fire(new StepStartedEvent(stepName).withTitle(stepName));
        K result;
        try {
            result = supplier.get();
        } catch (Throwable e) {
            Allure.LIFECYCLE.fire(new StepFailureEvent().withThrowable(e));
            throw e;
        } finally {
            Allure.LIFECYCLE.fire(new StepFinishedEvent());
        }
        return result;
    }
}
