package ru.yandex.quasar.fakes

import android.content.res.Resources
import org.mockito.kotlin.mock

class FakeResources : Resources(mock(), mock(), mock()) {
    override fun getDimensionPixelSize(id: Int): Int {
        return id
    }

    override fun getString(id: Int): String {
        return id.toString()
    }
}
