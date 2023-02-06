package ru.yandex.metrika.common.test.medium;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import ru.yandex.autotests.irt.testutils.beandiffer2.Diff;
import ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategy;
import ru.yandex.autotests.irt.testutils.beandiffer2.differ.ListDiffer;

import static ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategies.onlyExpectedFields;

public class OrderedListDiffer extends ListDiffer {

    private final Comparator comparator;

    public static DefaultCompareStrategy orderedListCompareStrategy(Comparator comparator) {
        return onlyExpectedFields().forClasses(ArrayList.class).useDiffer(new OrderedListDiffer(comparator));
    }

    private OrderedListDiffer(Comparator comparator) {
        this.comparator = comparator;
    }

    @Override
    public List<Diff> compare(Object actual, Object expected) {
        sortList(actual);
        sortList(expected);

        return super.compare(actual, expected);
    }

    private void sortList(Object list) {
        ((List<?>) list).sort(comparator);
    }

}
