package com.yandex.io.sdk.config

import org.hamcrest.MatcherAssert
import org.hamcrest.Matchers
import org.json.JSONObject
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class ConfigsMergerTest {

    private val configsMerger = ConfigsMerger()

    @Test
    fun `test merge on level 1`() {
        val configsContainerOld = configsMerger.convertToConfigsContainer(JSONObject(MERGE_LEVEL_1_JSON_OBJECT_OLD))
        val configsContainerNew = configsMerger.convertToConfigsContainer(JSONObject(MERGE_LEVEL_1_JSON_OBJECT_NEW))
        val configsContainerFinal = configsMerger.convertToConfigsContainer(JSONObject(MERGE_LEVEL_1_JSON_OBJECT_FINAL))
        val configsContainerMerged = configsMerger.mergeConfigs(configsContainerOld, configsContainerNew)
        MatcherAssert.assertThat(
            configsContainerMerged,
            Matchers.equalTo(configsContainerFinal)
        )
    }

    @Test
    fun `test merge on level 3`() {
        val configsContainerOld = configsMerger.convertToConfigsContainer(JSONObject(MERGE_LEVEL_3_JSON_OBJECT_OLD))
        val configsContainerNew = configsMerger.convertToConfigsContainer(JSONObject(MERGE_LEVEL_3_JSON_OBJECT_NEW))
        val configsContainerFinal = configsMerger.convertToConfigsContainer(JSONObject(MERGE_LEVEL_3_JSON_OBJECT_FINAL))
        val configsContainerMerged = configsMerger.mergeConfigs(configsContainerOld, configsContainerNew)
        MatcherAssert.assertThat(
            configsContainerMerged,
            Matchers.equalTo(configsContainerFinal)
        )
    }

    @Test
    fun `test rewrite on level 3`() {
        val configsContainerOld = configsMerger.convertToConfigsContainer(JSONObject(REWRITE_LEVEL_3_JSON_OBJECT_OLD))
        val configsContainerNew = configsMerger.convertToConfigsContainer(JSONObject(REWRITE_LEVEL_3_JSON_OBJECT_NEW))
        val configsContainerFinal = configsMerger.convertToConfigsContainer(JSONObject(REWRITE_LEVEL_3_JSON_OBJECT_FINAL))
        val configsContainerMerged = configsMerger.mergeConfigs(configsContainerOld, configsContainerNew)
        MatcherAssert.assertThat(
            configsContainerMerged,
            Matchers.equalTo(configsContainerFinal)
        )
    }

    companion object {
        private const val MERGE_LEVEL_1_JSON_OBJECT_OLD = """
            {
                "level1": {
                    "key1": "value1",
                    "key2": 1
                }
            }
        """
        private const val MERGE_LEVEL_1_JSON_OBJECT_NEW = """
            {
                "level1": {
                    "key3": false,
                    "key4": []
                }
            }
        """
        private const val MERGE_LEVEL_1_JSON_OBJECT_FINAL = """
            {
                "level1": {
                    "key1": "value1",
                    "key2": 1,
                    "key3": false,
                    "key4": []
                }
            }
        """

        private const val MERGE_LEVEL_3_JSON_OBJECT_OLD = """
            {
                "level1": {
                    "level2": {
                        "level3": {
                            "key1": "value1"
                        }
                    }
                }
            }
        """
        private const val MERGE_LEVEL_3_JSON_OBJECT_NEW = """
            {
                "level1": {
                    "level2": {
                        "level3": {
                            "key2": "value2"
                        }
                    }
                }
            }
        """
        private const val MERGE_LEVEL_3_JSON_OBJECT_FINAL = """
            {
                "level1": {
                    "level2": {
                        "level3": {
                            "key1": "value1",
                            "key2": "value2"
                        }
                    }
                }
            }
        """

        private const val REWRITE_LEVEL_3_JSON_OBJECT_OLD = """
            {
                "level1": {
                    "level2": {
                        "level3": {
                            "key": "value1"
                        }
                    }
                }
            }
        """
        private const val REWRITE_LEVEL_3_JSON_OBJECT_NEW = """
            {
                "level1": {
                    "level2": {
                        "level3": {
                            "key": "value2"
                        }
                    }
                }
            }
        """
        private const val REWRITE_LEVEL_3_JSON_OBJECT_FINAL = """
            {
                "level1": {
                    "level2": {
                        "level3": {
                            "key": "value2"
                        }
                    }
                }
            }
        """
    }
}
