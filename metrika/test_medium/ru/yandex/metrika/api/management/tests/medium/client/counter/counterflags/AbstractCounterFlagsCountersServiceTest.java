package ru.yandex.metrika.api.management.tests.medium.client.counter.counterflags;

import java.util.List;

import org.junit.runners.Parameterized;
import org.springframework.beans.factory.annotation.Autowired;

import ru.yandex.metrika.api.management.client.counter.CounterEdit;
import ru.yandex.metrika.api.management.client.counter.CounterFlags;
import ru.yandex.metrika.api.management.client.counter.CountersService;
import ru.yandex.metrika.api.management.client.external.CounterField;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.CounterMirrorE;

import static ru.yandex.metrika.CommonTestsHelper.FAKE_USER;

public abstract class AbstractCounterFlagsCountersServiceTest extends AbstractCounterFlagsTest {

    @Autowired
    protected CountersService countersService;
    private static int id = 0;

    protected static final List<CounterField> fields = List.of(CounterField.webvisor, CounterField.mirrors, CounterField.counter_flags);

    protected CounterFull createCounterWithFlags(CounterFlags counterFlags) {
        var counter = getSomeCounter();
        counter.setCounterFlags(counterFlags);
        return countersService.save(FAKE_USER, FAKE_USER, counter, fields, false);
    }

    private static CounterFull getSomeCounter() {
        var counter = new CounterFull();
        return setBasicDataToCounter(counter);
    }

    protected static CounterEdit getCounterEdit() {
        return new CounterEdit();
    }

    @Parameterized.Parameters(name = "{0}")
    public static List<Object[]> getAllCounterFlagsVariationsWithExpectedUploadingsResults() {
        return getAllCounterFlagsVariationsWithExpectedUploadingsResults(null);
    }

    static CounterFull setBasicDataToCounter(CounterFull counter) {
        int id = AbstractCounterFlagsCountersServiceTest.id++;
        counter.setName("counter's name " + id);
        counter.setSite2(new CounterMirrorE("example.com"));
        return counter;
    }
}
