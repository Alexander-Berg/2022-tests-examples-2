package ru.yandex.quasar.fakes

import ru.yandex.quasar.protobuf.QuasarProto
import ru.yandex.quasar.transport.QuasarConnector

class FakeQuasarConnector : QuasarConnector(FAKE_SERVICE_NAME, FakeConfiguration().apply { initialize(FAKE_CONFIG) }) {
    override fun start() {}

    /**
     * Send message to all subscribers of this connector
     */
    fun receiveQuasarMessage(message: QuasarProto.QuasarMessage) {
        receiveValue(message)
    }

    override fun send(message: QuasarProto.QuasarMessage?) { }

    companion object {
        const val FAKE_SERVICE_NAME = "fake"
        const val FAKE_CONFIG = "{'fake': {'port': 4242}}"
    }
}
