package ru.yandex.autotests.morda.steps;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.hamcrest.Matcher;
import org.hamcrest.StringDescription;
import org.openqa.selenium.internal.WrapsElement;
import ru.yandex.autotests.morda.steps.attach.AttachmentUtils;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.client.Client;
import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static org.junit.Assert.fail;
import static ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory.cookieUtils;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.timeoutHasExpired;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.isDisplayed;
import static ru.yandex.qatools.htmlelements.matchers.decorators.MatcherDecoratorsBuilder.should;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 07/04/15
 */
public class CheckSteps {


    private static <T> void innerCheck(T object, Matcher<? super T> matcher) throws JsonProcessingException {
        JsonNode node = new ObjectMapper().convertValue(object, JsonNode.class);

        String attach;

        if (node.getNodeType().equals(JsonNodeType.OBJECT)) {
            ObjectNode tmpNode = node.deepCopy();

            List<JsonNodeType> removeTypes = asList(JsonNodeType.ARRAY, JsonNodeType.OBJECT, JsonNodeType.POJO);

            node.fieldNames().forEachRemaining(e -> {
                JsonNodeType eType = tmpNode.get(e).getNodeType();
                if (removeTypes.contains(eType)) {
                    tmpNode.remove(e);
                    tmpNode.put(e, "[" + eType.toString().toLowerCase() + " removed]");
                }
            });

            attach = "***** DATA: *****\n" + new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(tmpNode) +
                    "\n\n***** CHECK: ***** \n" + matcher.toString() + "\n";
        } else {
            attach = "***** DATA: *****\n" + new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(node) +
                    "\n\n***** CHECK: ***** \n" + matcher.toString() + "\n";
        }

        if (!matcher.matches(object)) {
            StringDescription error = new StringDescription();
            matcher.describeMismatch(object, error);
            attach += "\n***** ERROR: *****\n" + error.toString();
            System.out.println(attach);
            AttachmentUtils.attachText("check.info", attach);
            fail(error.toString());
        }

        System.out.println(attach);
        AttachmentUtils.attachText("check.info", attach);

        assertThat(object, matcher);
    }

    public static <T> void checkBean(T t, Matcher<? super T> matcher) {
        try {
            innerCheck(t, matcher);
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }

    @Step("Element \"{0}\" should exist")
    public static Runnable shouldExistElement(WrapsElement element) {
        return () -> {
            assertThat(element.toString(), element,
                    should(exists()).whileWaitingUntil(timeoutHasExpired(5000L)));
        };
    }

    @Step("Should see element \"{0}\"")
    public static Runnable shouldSeeElement(WrapsElement element) {
        return () -> {
            assertThat(element.toString(), element,
                    should(exists()).whileWaitingUntil(timeoutHasExpired(5000L)));
            assertThat(element.toString(), element,
                    should(isDisplayed()).whileWaitingUntil(timeoutHasExpired(5000L)));
        };
    }

    @Step("Should not see element \"{0}\"")
    public static Runnable shouldNotSeeElement(WrapsElement element) {
        return () -> {
            if (exists().matches(element)) {
                assertThat(element.toString(), element,
                        should(not(isDisplayed())).whileWaitingUntil(timeoutHasExpired(5000L)));
            }
        };
    }

    @Step("Element \"{0}\": {1}")
    public static <T> Runnable shouldSeeElementMatchingTo(T element, Matcher<? super T> matcher) {
        return () -> {
            assertThat(element.toString(), element,
                    should(matcher).whileWaitingUntil(timeoutHasExpired(5000L)));
        };
    }

    @Step("Should see cookie \"{1}\"")
    public static Runnable shouldSeeCookie(Client client, String cookieName, String cookieDomain) {
        return () -> assertThat(cookieUtils(client).getCookieNamed(cookieName, cookieDomain), notNullValue());
    }

    public static String url(String url, String scheme) {
        if (url.startsWith("//")) {
            return scheme + ":" + url;
        }
        return url;
    }

}
