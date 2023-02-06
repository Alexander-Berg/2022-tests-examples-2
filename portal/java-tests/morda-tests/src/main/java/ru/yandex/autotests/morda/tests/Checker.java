package ru.yandex.autotests.morda.tests;

import java.util.HashSet;
import java.util.Set;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/08/16
 */
public interface Checker<T> {

    default void checkExists(T t) {}

    default Set<String> getStaticUrls(T t) {return new HashSet<>();}

    default Set<String> getUrlsToPing(T t) {return new HashSet<>();}

    default Set<String> getAllUrls(T t) {return new HashSet<>();}

}
