package ru.yandex.autotests.morda.rules.errorcollector;

import org.apache.commons.lang3.StringUtils;
import org.junit.rules.Verifier;

import static org.junit.Assert.fail;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 06/04/15
 */
public class HierarchicalErrorCollectorRule extends Verifier {
    private HierarchicalErrorCollector collector;

    public HierarchicalErrorCollectorRule() {
        collector = HierarchicalErrorCollector.collector();
    }

    public HierarchicalErrorCollector getCollector() {
        this.collector = HierarchicalErrorCollector.collector();
        return collector;
    }

    @Override
    protected void verify() throws Throwable {
        collector.collect();

        if (collector.getErrors().size() > 0) {

            String str = StringUtils.join(collector.getErrors(), "\n\n");

            fail("Какие-то упячки =/ \n\n" + str);
        }
    }
}
