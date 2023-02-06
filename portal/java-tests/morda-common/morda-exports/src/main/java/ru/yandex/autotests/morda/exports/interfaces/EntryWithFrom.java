package ru.yandex.autotests.morda.exports.interfaces;

import org.joda.time.LocalDateTime;

/**
 * User: asamar
 * Date: 17.01.17
 */
public interface EntryWithFrom extends Entry {
    LocalDateTime getFrom();
}
