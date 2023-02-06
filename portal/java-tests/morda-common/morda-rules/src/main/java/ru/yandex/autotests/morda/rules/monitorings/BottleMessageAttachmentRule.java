package ru.yandex.autotests.morda.rules.monitorings;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.log4j.Logger;
import org.junit.runner.Description;
import ru.yandex.qatools.elliptics.Elliptics;
import ru.yandex.terra.junit.rules.BottleMessageRule;

import java.util.ArrayList;
import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 23/11/14
 */
public class BottleMessageAttachmentRule extends BottleMessageRule {
    private static final String ELLIPTICS_DIR = "morda/monitorings/json/%s.json";
    private static final Logger LOG = Logger.getLogger(BottleMessageAttachmentRule.class);
    private static final ObjectMapper OBJECT_MAPPER;
    static {
        OBJECT_MAPPER= new ObjectMapper();
        OBJECT_MAPPER.enable(SerializationFeature.INDENT_OUTPUT);
    }

    private List<MetaData> metas;
    private Elliptics elliptics;

    public BottleMessageAttachmentRule() {
        this.elliptics = new Elliptics();
        this.metas = new ArrayList<>();
    }

    @Override
    protected void failed(Throwable e, Description description) {
        for (MetaData metaData : metas) {
            try {
                Object jsonInObject = OBJECT_MAPPER.readValue(metaData.getValue(), Object.class);
                String json = OBJECT_MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(jsonInObject);

                String url = elliptics.put(json,
                        String.format(ELLIPTICS_DIR, RandomStringUtils.random(16, true, false)));
                LOG.info("Uploaded meta data: " + url);
                this.addMeta(metaData.getName(), metaData.getName(), url);
            } catch (Exception e1) {
                LOG.error("Failed to upload meta data in json \n", e1);
                String url = elliptics.put(metaData.getValue(),
                        String.format(ELLIPTICS_DIR, RandomStringUtils.random(16, true, false)));
                LOG.info("Uploaded meta data: " + url);
                this.addMeta(metaData.getName(), metaData.getName(), url);
            }
        }
        super.failed(e, description);
    }

    public void addMeta(String name, String value) {
        metas.add(new MetaData(name, value));
    }

    public static class MetaData {
        private String name;
        private String value;

        public MetaData(String name, String value) {
            this.name = name;
            this.value = value;
        }

        public String getValue() {
            return value;
        }

        public void setValue(String value) {
            this.value = value;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }
    }

}
