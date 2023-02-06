package ru.yandex.autotests.metrika.appmetrica.matchers;

import ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath;

import java.util.List;

public final class JoinedBeanFieldPath implements BeanFieldPath {

    private final BeanFieldPath subject;

    private static BeanFieldPath joinPaths(BeanFieldPath prefix, BeanFieldPath suffix) {
        BeanFieldPath result = prefix;
        for (String element : suffix.split()) {
            result = result.join(element);
        }

        return result;
    }

    public JoinedBeanFieldPath(BeanFieldPath prefix, BeanFieldPath suffix) {
        this(joinPaths(prefix, suffix));
    }

    private JoinedBeanFieldPath(BeanFieldPath subject) {
        this.subject = subject;
    }

    @Override
    public List<String> split() {
        return subject.split();
    }

    @Override
    public BeanFieldPath join(String childName) {
        return subject.join(childName);
    }

    @Override
    public boolean matches(BeanFieldPath regexPath) {
        return subject.matches(regexPath);
    }

    @Override
    public int compareTo(BeanFieldPath o) {
        return subject.compareTo(o);
    }

    @Override
    public String toString() {
        return subject.toString();
    }
}
