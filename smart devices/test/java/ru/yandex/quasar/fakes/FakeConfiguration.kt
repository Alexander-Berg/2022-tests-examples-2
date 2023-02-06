package ru.yandex.quasar.fakes

import ru.yandex.quasar.core.Configuration

class FakeConfiguration : Configuration() {
    fun initialize(data: String) {
        init(data)
    }
}
