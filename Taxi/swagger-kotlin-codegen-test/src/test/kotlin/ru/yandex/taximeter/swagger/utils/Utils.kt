package ru.yandex.taximeter.swagger.utils

import org.intellij.lang.annotations.Language

object Utils {
    @Language("json")
    const val testOneResponseJson = """
        {
            "version": "v1",
            "payload": "payload1"
        }
    """

    @Language("json")
    const val testTwoResponseJson = """
        {
            "version": "v2",
            "count": 123
        }
    """

    @Language("json")
    const val testSealedSuccessJson = """
        {
            "type": "success",
            "payload": "success"
        }
    """

    @Language("json")
    const val testSealedFailureJson = """
        {
            "type": "failure",
            "message": "failure"
        }
    """

    @Language("json")
    const val testSealedByDiscriminatorSuccessJson = """
        {
            "type": "success",
            "message": "success"
        }
    """

    @Language("json")
    const val testSealedByRefEnumDiscriminatorSuccessJson = """
        {
            "type": "success_status",
            "payload": "success"
        }
    """

    @Language("json")
    const val testSealedByDiscriminatorFailureJson = """
        {
            "type": "failure",
            "message": "failure"
        }
    """

    @Language("json")
    const val testBuiltInJson = """
        {
            "count": 321,
            "payload": "builtin"
        }
    """

    @Language("json")
    const val testBuiltInAllOfJson = """
        {
            "group_code": "group_code",
            "login": "login",
            "password": "password"
        }
    """

    @Language("json")
    const val commonResponse = """
        {
            "version": "v1"
        }
    """

    @Language("json")
    const val error404 = """
        {
            "code": 404,
            "message": "error 404"
        }
    """

    @Language("json")
    const val additionalPropertyWithCustomTypeResponse = """
        {
            "version": "123",
            "check_results": {
              "231": {
                "payload": "ok"
              }
            }
        }
    """
}