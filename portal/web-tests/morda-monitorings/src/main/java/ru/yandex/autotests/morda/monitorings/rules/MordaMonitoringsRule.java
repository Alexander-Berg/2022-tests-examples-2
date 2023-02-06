package ru.yandex.autotests.morda.monitorings.rules;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.gson.GsonBuilder;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.runner.Description;
import org.openqa.selenium.WebDriver;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import ru.yandex.qatools.elliptics.Elliptics;
import ru.yandex.terra.junit.rules.BottleMessageRule;

import java.util.ArrayList;
import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 23/11/14
 */
public class MordaMonitoringsRule extends BottleMessageRule {
    private static final String ELLIPTICS_DIR = "morda/monitorings/json/%s.json";
    private static final Logger LOG = LoggerFactory.getLogger(MordaMonitoringsRule.class);

    private List<MetaData> metas;
    private Elliptics elliptics;

    public MordaMonitoringsRule() {
        this.elliptics = new Elliptics();
        this.metas = new ArrayList<>();
    }

    public MordaMonitoringsRule(WebDriver driver) {
        super(driver);
        this.elliptics = new Elliptics();
        this.metas = new ArrayList<>();
    }

    @Override
    protected void failed(Throwable e, Description description) {
        for (MetaData metaData : metas) {
            try {
                ObjectMapper mapper = new ObjectMapper();
                Object jsonInObject = mapper.readValue(metaData.getValue(), Object.class);
                String json = new GsonBuilder().setPrettyPrinting().create().toJson(jsonInObject);

                String url = elliptics.put(json,
                        String.format(ELLIPTICS_DIR, RandomStringUtils.random(16, true, false)));
                LOG.info("Uploaded meta data: " + url);
                this.addMeta(metaData.getName(), metaData.getName(), url);
            } catch (Exception e1) {
                LOG.error("Failed to upload meta data \n", e1);
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
