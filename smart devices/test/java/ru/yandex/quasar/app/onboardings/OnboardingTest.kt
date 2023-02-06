package ru.yandex.quasar.app.onboardings

import com.google.gson.Gson
import org.assertj.core.api.Assertions
import org.junit.Test

class OnboardingTest {
    private val onboarding = Onboarding().apply {
        id = "test"
        content = OnboardingContent().apply {
            layoutUrl = "https://layout"
            videoUrl = "https://video"
            splashDiv = "div"
            talkienActions = listOf("skip", "play")
        }
        conditions = OnboardingConditions().apply {
            intent = "show_home"
            scenario = "ether"
            minSoftwareVersion = "2.3.3"
            requiredExperiments = setOf("ether", "mordovia")
        }
    }

    private val json = """
        {
            "id": "test",
            "content": {
                "layout": "https://layout",
                "video": "https://video",
                "splash": "div",
                "actions": ["skip", "play"]
            },
            "conditions": {
                "intent": "show_home",
                "scenario": "ether",
                "software": "2.3.3",
                "experiments": ["ether", "mordovia"]
            }
        }
    """.replace(Regex("\\s+"), "")

    private val gson = Gson()

    @Test
    fun jsonSerialization_shouldWork_inGeneralCase() {
        Assertions
            .assertThat(gson.toJson(onboarding).replace(Regex("\\s+"), ""))
            .isEqualTo(json)
    }

    @Test
    fun jsonDeserialization_shouldWork_inGeneralCase() {
        Assertions
            .assertThat(gson.fromJson(json, Onboarding::class.java))
            .isEqualToComparingFieldByFieldRecursively(onboarding)
    }
}