package ru.yandex.quasar.centaur_app

import ru.yandex.quasar.centaur_app.metrica.Event
import ru.yandex.quasar.centaur_app.metrica.IMetricaReporter

class FakeMetricaReporter: IMetricaReporter {
    override fun report(event: Event) {
        //
    }
}
