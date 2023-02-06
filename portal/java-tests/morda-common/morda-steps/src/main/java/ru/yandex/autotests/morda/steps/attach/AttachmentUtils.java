package ru.yandex.autotests.morda.steps.attach;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import org.apache.commons.lang3.StringUtils;
import org.apache.log4j.Logger;
import org.jsoup.Jsoup;
import ru.yandex.qatools.allure.annotations.Attachment;

import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29/07/16
 */
public class AttachmentUtils {

    private static final Logger LOGGER = Logger.getLogger(AttachmentUtils.class);
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper()
            .configure(SerializationFeature.INDENT_OUTPUT, true);

    @Attachment(value = "{0}", type = "application/json")
    public static String attachJson(String name, String json) throws IOException {
        Object object = OBJECT_MAPPER.readValue(json, Object.class);
        return OBJECT_MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(object);
    }

    @Attachment(value = "{0}", type = "text/plain")
    public static String attachText(String name, String text) {
        return text;
    }

    @Attachment(value = "{0}", type = "text/plain")
    public static String attachHtmlAsText(String name, String html) {
        LOGGER.info("Attaching file \"" + name + "\"");
        return Jsoup.parse(html).toString();
    }

    @Attachment(value = "{0}", type = "text/plain")
    public static String attachText(String name, List<String> text) {
        String t = StringUtils.join(text, "\n");
        LOGGER.info(name + "\n" + t);
        return t;
    }

    @Attachment(value = "{0}", type = "application/json")
    public static String attachJson(String name, Object object) {
        try {
            System.out.println(OBJECT_MAPPER.writeValueAsString(object));
            return OBJECT_MAPPER.writeValueAsString(object);
        } catch (JsonProcessingException e) {
            LOGGER.error(e.getMessage(), e);
            return "";
        }
    }

    @Attachment(value = "{0}", type = "application/json")
    public static String attachJson(String name, List<Object> objects) throws JsonProcessingException {
        List<String> strings = objects.stream()
                .map(s -> {
                    try {
                        return OBJECT_MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(objects);
                    } catch (JsonProcessingException e) {
                        LOGGER.error(e.getMessage(), e);
                        return "";
                    }
                })
                .collect(Collectors.toList());

        return StringUtils.join(strings, "\n");
    }

}
