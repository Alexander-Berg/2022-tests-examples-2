import logging
import requests


class VideohubHandsTesterFailureException(Exception):
    pass


class _VideohubHandsTester:

    def __init__(self, checker):
        self.isError = False
        self.checker = checker

    def __call__(self, testName, requestUrl, requiredSchema, fields_paths=[]):
        response = requests.get(requestUrl).json()

        if self.checker(response, requiredSchema, testName) == 2:
            self.isError = self.isError or True
            if fields_paths != []:
                return [None] * len(fields_paths)
        else:
            answer = []
            for field_path in fields_paths:
                field = response
                for f in field_path.split("."):
                    field = field[f]
                answer.append(field)
            return answer

    def check(self):
        if self.isError:
            logging.error("One or more tests failed")
        else:
            logging.info("ALL TESTS PASSED SUCCESSFULLY")


DEFAULT_VIDEOHUB_GROUP_PARAMS = {"docsMinCount": 1, "docsMaxCount": 20}
DEFAULT_VITRINA_GROUP_PARAMS = {"netflix": {"categoriesMinCount": 1, "categoriesMaxCount": 1, "category": {"docsMinCount": 1, "docsMaxCount": 20}}}


class SchemaFactory(object):

    @staticmethod
    def GetVideohubDocSchema():
        return {
            "type": "object",
            "properties": {
                "Url": {"type": "string"},
                "onto_id": {"type": "string"},
                "percentage_score": {"type": "number"}
            },
            "required": ["Url"],
            "additionalProperties": False
        }

    @staticmethod
    def GetVideohubGroupSchema(params=DEFAULT_VIDEOHUB_GROUP_PARAMS):
        return {
            "type": "object",
            "properties": {
                "IsBlogger": {"type": "boolean"},
                "Poster": {"type": "boolean"},
                "CacheHash": {"type": "string"},
                "CategId": {"type": "string"},
                "CategTagId": {"type": "string"},
                "GroupId": {"type": "string"},
                "GroupType": {"type": "string", "enum": ["videohub"]},
                "Type": {"type": "string"},
                "Thumbnail": {
                    "type": "object",
                    "properties": {
                        "thumbnail": {"type": "string"},
                        "publisher_avatar": {"type": "string"},
                        "publisher_background": {"type": "string"},
                        "publisher_logo": {"type": "string"}
                    },
                    "additionalProperties": False
                },
                "Docs": {
                    "type": "array",
                    "minItems": params["docsMinCount"],
                    "maxItems": params["docsMaxCount"],
                    "items": SchemaFactory.GetVideohubDocSchema(),
                    "additionalItems": False,
                    "uniqueItems": True
                }
            },
            "required": ["GroupType"],
            "additionalProperties": False
        }

    @staticmethod
    def GetVitrinaNetflixQuerySchema():
        return {
            "type": "object",
            "properties": {
                "percentage_score": {"type": "number"},
                "ontoid": {"type": "string"}
            },
            "required": ["percentage_score", "ontoid"],
            "additionalProperties": False
        }

    @staticmethod
    def GetVitrinaNetflixCategorySchema(params):
        return {
            "type": "object",
            "properties": {
                "type": {"type": "number"},
                "title": {"type": "string"},
                "weight": {"type": "number"},
                "queries": {
                    "type": "array",
                    "minItems": params["docsMinCount"],
                    "maxItems": params["docsMaxCount"],
                    "items": SchemaFactory.GetVitrinaNetflixQuerySchema(),
                    "additionalItems": False,
                    "uniqueItems": True
                }
            },
            "required": ["type", "title", "weight", "queries"],
            "additionalProperties": False
        }

    @staticmethod
    def GetVitrinaNetflixSchema(params):
        return {
            "type": "object",
            "properties": {
                "categories": {
                    "type": "array",
                    "minItems": params["categoriesMinCount"],
                    "maxItems": params["categoriesMaxCount"],
                    "items": SchemaFactory.GetVitrinaNetflixCategorySchema(params["category"]),
                    "additionalItems": False
                }
            },
            "required": ["categories"],
            "additionalProperties": False
        }

    @staticmethod
    def GetVitrinaGroupSchema(params=DEFAULT_VITRINA_GROUP_PARAMS):
        return {
            "type": "object",
            "properties": {
                "CacheHash": {"type": "string"},
                "GroupType": {"type": "string", "enum": ["vitrina"]},
                "_SerpData": {
                    "type": "object",
                    "properties": {
                        "netflix": SchemaFactory.GetVitrinaNetflixSchema(params["netflix"])
                    },
                    "additionalProperties": False
                },
                "_SerpInfo": {
                    "type": "object",
                    "properties": {
                        "subtype": {"type": "string"},
                        "type": {"type": "string"},
                        "format": {"type": "string"}
                    },
                    "required": ["subtype", "type", "format"],
                    "additionalProperties": False
                }
            },
            "required": ["GroupType", "CacheHash"],
            "additionalProperties": False
        }

    @staticmethod
    def GetDefaultResponseSchema(params, groupsSchemas):
        return {
            "type": "object",
            "properties": {
                "reqid": {"type": "string"},
                "type": {"type": "string"},
                "Groups": {
                    "type": "array",
                    "maxItems": params["maxGroupsCount"],
                    "minItems": params["minGroupsCount"],
                    "items": {
                        "oneOf": groupsSchemas
                    },
                    "additionalItems": False
                }
            },
            "required": ["type", "Groups", "reqid"]
        }


class VideohubHandsTester:

    def __init__(self, checker, base_url, custom_cgi):
        self.checker = checker
        self.base_url = base_url
        self.custom_cgi = custom_cgi
        self.tester = _VideohubHandsTester(self.checker)

    def _testPagesSupertagRequest(self, supertag, docsSchemas, pages=3, carousels_per_page=10):
        cache_hash = None
        for page in range(0, pages):
            carousels_per_current_page = None
            if type(carousels_per_page) == int:
                carousels_per_current_page = carousels_per_page
            elif type(carousels_per_page) == list:
                carousels_per_current_page = carousels_per_page[page]
            else:
                raise Exception("Unexpected type of carousels_per_page: {}. Expected int or list.".format(type(carousels_per_page)))
            cache_hash = self.tester(
                "{}_page-{}".format(supertag, page),
                "{}/video/videohub?client=vh&delete_filtered=0&enable_channels=1&from=efir&locale=ru&request={}&limit={}&offset={}&{}".format(
                    self.base_url,
                    supertag,
                    carousels_per_current_page,
                    carousels_per_current_page * page,
                    self.custom_cgi + "&cache_hash={}".format(cache_hash)),
                SchemaFactory.GetDefaultResponseSchema(
                    {"maxGroupsCount": carousels_per_current_page, "minGroupsCount": carousels_per_current_page},
                    docsSchemas
                ),
                ["CacheHash"]
            )[0]

    def test(self, skip_failed_music_request=True):
        self._testPagesSupertagRequest("videohub", [SchemaFactory.GetVideohubGroupSchema(), SchemaFactory.GetVitrinaGroupSchema()])
        self._testPagesSupertagRequest("blogger", [SchemaFactory.GetVideohubGroupSchema()])
        self._testPagesSupertagRequest("movie", [SchemaFactory.GetVideohubGroupSchema(), SchemaFactory.GetVitrinaGroupSchema()])
        self._testPagesSupertagRequest("cyber_sport", [SchemaFactory.GetVideohubGroupSchema()], pages=1)
        self._testPagesSupertagRequest("series", [SchemaFactory.GetVideohubGroupSchema(), SchemaFactory.GetVitrinaGroupSchema()])
        self._testPagesSupertagRequest("sport", [SchemaFactory.GetVideohubGroupSchema()], pages=2)
        try:
            self._testPagesSupertagRequest("music", [SchemaFactory.GetVideohubGroupSchema()])
        except requests.exceptions.ConnectionError:
            if skip_failed_music_request:
                pass
            else:
                raise
        self._testPagesSupertagRequest("special_event", [SchemaFactory.GetVideohubGroupSchema()], pages=1)
        self._testPagesSupertagRequest("subscription", [SchemaFactory.GetVideohubGroupSchema()], pages=1, carousels_per_page=9)

        self.tester(
            "BloggersRequestWithCustomLimit",
            "{}/video/videohub?client=vh&request=blogger&delete_filtered=0&enable_channels=1&from=efir&limit=15&locale=ru&offset=0&{}".format(self.base_url, self.custom_cgi),
            SchemaFactory.GetDefaultResponseSchema(
                {"maxGroupsCount": 15, "minGroupsCount": 15},
                [SchemaFactory.GetVideohubGroupSchema()]
            )
        )

        self.tester(
            "MovieRequestWithCustomLimit",
            "{}/video/videohub?client=vh&request=movie&delete_filtered=0&enable_channels=1&from=efir&limit=20&locale=ru&offset=0&{}".format(self.base_url, self.custom_cgi),
            SchemaFactory.GetDefaultResponseSchema(
                {"maxGroupsCount": 20, "minGroupsCount": 20},
                [SchemaFactory.GetVitrinaGroupSchema(), SchemaFactory.GetVideohubGroupSchema()]
            )
        )

        self.tester.check()


def check(json_obj, schema, testName):
    from jsonschema import validate, exceptions
    try:
        validate(json_obj, schema)
    except exceptions.ValidationError as e:
        logging.error('TEST {} FAILED: ValidationError:\n"""{}"""'.format(testName, e.message))
        return 2
    except Exception as e:
        logging.error('ERROR ON TEST {}:'.format(testName))
        raise e
        return 1
    else:
        logging.info("TEST {} SUCCESS".format(testName))
        return 0


if __name__ == '__main__':
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    VideohubHandsTester(check, "http://video-http-apphost.hamster.yandex.ru", "yandexuid=2&region=225&vitrina_filter=vh").test()
