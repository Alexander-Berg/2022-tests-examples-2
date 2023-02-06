package ru.yandex.quasar.shadows

import org.robolectric.annotation.Implementation
import org.robolectric.annotation.Implements
import ru.yandex.quasar.core.utils.ThreadUtil

@Implements(ThreadUtil::class)
object ShadowThreadUtil {
    @Implementation
    @JvmStatic
    fun isMainThread(): Boolean {
        return true
    }
}
