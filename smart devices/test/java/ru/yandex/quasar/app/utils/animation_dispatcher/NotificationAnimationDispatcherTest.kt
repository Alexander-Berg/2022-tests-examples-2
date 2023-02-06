package ru.yandex.quasar.app.utils.animation_dispatcher

import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.mock
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.shadows.ShadowLogger

@RunWith(RobolectricTestRunner::class)
@Config(shadows = [ShadowLogger::class], instrumentedPackages = ["ru.yandex.quasar.util"])
class NotificationAnimationDispatcherTest {

    private val emptyAnimation = DefaultAnimation {}

    @Test
    fun when_addEmptyAnimations_then_sizeIsCalculatedCorrectly() {
        val dispatcher = NotificationAnimationDispatcher()
        dispatcher.pushNextAnimation(emptyAnimation)
        dispatcher.pushNextAnimation(emptyAnimation)

        Assert.assertEquals(2, dispatcher.animationQueue.size)
    }

    @Test
    fun when_addNotificationAnimations_then_mergeIsCalculatedCorrectly() {
        val dispatcher = NotificationAnimationDispatcher()

        val firstChangeAnimation = ChangeNotificationCountAnimation(1, 2, mock())
        val secondChangeAnimation = ChangeNotificationCountAnimation(2, 3, mock())
        val thirdChangeAnimation = ChangeNotificationCountAnimation(3, 4, mock())
        val fourthChangeAnimation = ChangeNotificationCountAnimation(4, 5, mock())

        dispatcher.pushNextAnimation(firstChangeAnimation)
        dispatcher.pushNextAnimation(secondChangeAnimation)
        dispatcher.pushNextAnimation(thirdChangeAnimation)
        dispatcher.pushNextAnimation(fourthChangeAnimation)

        // we don't merge with first animation because it's already played
        Assert.assertEquals(2, (dispatcher.animationQueue.last as ChangeNotificationCountAnimation).oldCount)
        Assert.assertEquals(5, (dispatcher.animationQueue.last as ChangeNotificationCountAnimation).newCount)
        Assert.assertEquals(2, dispatcher.animationQueue.size)
    }

    @Test
    fun when_addAlternateAnimations_then_sizeIsCalculatedCorrectly() {
        val dispatcher = NotificationAnimationDispatcher()

        val firstChangeAnimation = ChangeNotificationCountAnimation(1, 2, mock())
        val secondChangeAnimation = ChangeNotificationCountAnimation(2, 3, mock())

        dispatcher.pushNextAnimation(emptyAnimation)
        dispatcher.pushNextAnimation(firstChangeAnimation)
        dispatcher.pushNextAnimation(emptyAnimation)
        dispatcher.pushNextAnimation(secondChangeAnimation)

        Assert.assertEquals(2, (dispatcher.animationQueue.last as ChangeNotificationCountAnimation).oldCount)
        Assert.assertEquals(3, (dispatcher.animationQueue.last as ChangeNotificationCountAnimation).newCount)

        Assert.assertEquals(4, dispatcher.animationQueue.size)
    }

    @Test
    fun when_addAlternateAnimations_then_mergeIsCalculatedCorrectly() {
        val dispatcher = NotificationAnimationDispatcher()

        val firstChangeAnimation = ChangeNotificationCountAnimation(1, 2, mock())
        val secondChangeAnimation = ChangeNotificationCountAnimation(2, 3, mock())
        val thirdChangeAnimation = ChangeNotificationCountAnimation(3, 4, mock())
        val fourthChangeAnimation = ChangeNotificationCountAnimation(4, 5, mock())

        dispatcher.pushNextAnimation(firstChangeAnimation)
        dispatcher.pushNextAnimation(secondChangeAnimation)
        dispatcher.pushNextAnimation(emptyAnimation)
        dispatcher.pushNextAnimation(thirdChangeAnimation)
        dispatcher.pushNextAnimation(fourthChangeAnimation)

        Assert.assertEquals(3, (dispatcher.animationQueue.last as ChangeNotificationCountAnimation).oldCount)
        Assert.assertEquals(5, (dispatcher.animationQueue.last as ChangeNotificationCountAnimation).newCount)

        Assert.assertEquals(4, dispatcher.animationQueue.size)
    }

    @Test
    fun when_addEndedNotificationAnimations_then_mergeIsCalculatedCorrectly() {
        val dispatcher = NotificationAnimationDispatcher()

        val firstChangeAnimation = ChangeNotificationCountAnimation(1, 2, mock())
        val secondChangeAnimation = ChangeNotificationCountAnimation(2, 3, mock())
        val thirdChangeAnimation = ChangeNotificationCountAnimation(3, 4, mock())
        val fourthChangeAnimation = ChangeNotificationCountAnimation(4, 5, mock())

        dispatcher.pushNextAnimation(emptyAnimation)
        dispatcher.pushNextAnimation(firstChangeAnimation)
        dispatcher.pushNextAnimation(secondChangeAnimation)
        dispatcher.pushNextAnimation(thirdChangeAnimation)
        dispatcher.pushNextAnimation(fourthChangeAnimation)

        Assert.assertEquals(1, (dispatcher.animationQueue.last as ChangeNotificationCountAnimation).oldCount)
        Assert.assertEquals(5, (dispatcher.animationQueue.last as ChangeNotificationCountAnimation).newCount)

        Assert.assertEquals(2, dispatcher.animationQueue.size)
    }

    @Test
    fun when_addFirstNotificationAnimations_then_mergeIsCalculatedCorrectly() {
        val dispatcher = NotificationAnimationDispatcher()

        val firstChangeAnimation = ChangeNotificationCountAnimation(1, 2, mock())
        val secondChangeAnimation = ChangeNotificationCountAnimation(2, 3, mock())
        val thirdChangeAnimation = ChangeNotificationCountAnimation(3, 4, mock())
        val fourthChangeAnimation = ChangeNotificationCountAnimation(4, 5, mock())

        dispatcher.pushNextAnimation(firstChangeAnimation)
        dispatcher.pushNextAnimation(secondChangeAnimation)
        dispatcher.pushNextAnimation(thirdChangeAnimation)
        dispatcher.pushNextAnimation(fourthChangeAnimation)
        dispatcher.pushNextAnimation(emptyAnimation)

        // we don't merge with first animation because it's already played
        Assert.assertEquals(2, (dispatcher.animationQueue[1] as ChangeNotificationCountAnimation).oldCount)
        Assert.assertEquals(5, (dispatcher.animationQueue[1] as ChangeNotificationCountAnimation).newCount)

        Assert.assertEquals(3, dispatcher.animationQueue.size)
    }
}
