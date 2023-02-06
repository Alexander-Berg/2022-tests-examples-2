package com.yandex.tv.common.utility.ui.tests.suites

import com.yandex.tv.common.device.utils.BoardUtils
import com.yandex.tv.common.utility.ui.tests.utils.ParentFilter
import org.junit.runner.Description

@Target(
    AnnotationTarget.ANNOTATION_CLASS,
    AnnotationTarget.CLASS,
    AnnotationTarget.FUNCTION,
    AnnotationTarget.PROPERTY_GETTER,
    AnnotationTarget.PROPERTY_SETTER
)
@Retention(AnnotationRetention.RUNTIME)
annotation class PlatformSuppress(val platforms: Array<String> = []) {

    class PlatformFilter : ParentFilter() {
        override fun evaluateTest(description: Description): Boolean {
            val testAnnotation = description.getAnnotation(PlatformSuppress::class.java)
            val classAnnotation = description.testClass.getAnnotation(PlatformSuppress::class.java)
            return isPlatformRequired(testAnnotation) && isPlatformRequired(classAnnotation)
        }

        override fun describe(): String {
            return "Skip tests annotated with @PlatformSuppress"
        }

        private fun isPlatformRequired(annotation: PlatformSuppress?): Boolean {
            return annotation == null || !BoardUtils.isBoard(*annotation.platforms)
        }
    }
}
