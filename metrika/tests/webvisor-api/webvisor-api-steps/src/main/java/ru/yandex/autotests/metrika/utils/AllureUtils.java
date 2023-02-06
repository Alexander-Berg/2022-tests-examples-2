package ru.yandex.autotests.metrika.utils;

import org.hamcrest.Matcher;

import ru.yandex.autotests.irt.testutils.allure.TestSteps;

/**
 * Created by konkov on 09.09.2014.
 */
public class AllureUtils {

    /**
     * обертка над TestSteps.assumeThat, нужна потому что TestSteps.assumeThat - generic и в сложных случаях,
     * когда actualResult, например, List<List<Double>> компилятор не может вывести тип для матчера.
     * Здесь используется Object и применимость матчера проверяется в run-time.
     *
     * @param assumeMessage - сообщение степа
     * @param actualResult - актуальное значение
     * @param matcher - матчер
     */
    public static void assumeThat(String assumeMessage, Object actualResult, Matcher matcher) {
        TestSteps.assumeThat(assumeMessage, actualResult, matcher);
    }

    /**
     * обертка над TestSteps.assertThat, нужна потому что TestSteps.assertThat - generic и в сложных случаях,
     * когда actualResult, например, List<List<Double>> компилятор не может вывести тип для матчера.
     * Здесь используется Object и применимость матчера проверяется в run-time.
     *
     * @param stepMessage - сообщение степа
     * @param actualResult - актуальное значение
     * @param matcher - матчер
     */
    public static void assertThat(String stepMessage, Object actualResult, Matcher matcher) {
        TestSteps.assertThat(stepMessage, actualResult, matcher);
    }

    public static void addTextAttachment(String title, String attachment) {
        ru.yandex.autotests.irt.testutils.allure.AllureUtils.addTextAttachment(title, attachment);
    }

    public static void addJsonAttachment(String title, String attachment) {
        ru.yandex.autotests.irt.testutils.allure.AllureUtils.addJsonAttachment(title, attachment);
    }

    public static void addCsvAttachment(String title, byte[] attachment) {
        ru.yandex.autotests.irt.testutils.allure.AllureUtils.addCsvAttachment(title, attachment);
    }

    public static void addXlsxAttachment(String title, byte[] attachment) {
        ru.yandex.autotests.irt.testutils.allure.AllureUtils.addXlsxAttachment(title, attachment);
    }

    public static void addTestParameter(String name, String value) {
        ru.yandex.autotests.irt.testutils.allure.AllureUtils.addTestParameter(name, value);
    }
}
