package com.yandex.tv.common.utility.test

import android.app.Activity
import android.content.ContentProvider
import org.robolectric.android.controller.ActivityController
import org.robolectric.android.controller.ComponentController
import org.robolectric.android.controller.ContentProviderController
import org.robolectric.shadows._Activity_
import org.robolectric.util.reflector.Reflector
import java.lang.reflect.Field

fun injectActivitySpy(activityController: ActivityController<*>, activity: Activity) {
    val componentField: Field = ComponentController::class.java.getDeclaredField("component")
    componentField.isAccessible = true
    componentField.set(activityController, activity)
    val _component_Field: Field = ActivityController::class.java.getDeclaredField("_component_")
    _component_Field.isAccessible = true
    _component_Field.set(activityController, Reflector.reflector(_Activity_::class.java, activity))
}

fun injectContentProviderSpy(provicerController: ContentProviderController<*>, provider: ContentProvider) {
    val contentProviderField: Field = ContentProviderController::class.java.getDeclaredField("contentProvider")
    contentProviderField.isAccessible = true
    contentProviderField.set(provicerController, provider)
}
