# https://wiki.yandex-team.ru/wall-e/guide/cms/#jsonschema

POST_RESPONSE = {
    "title": "Task as it was created by CMS",
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255,
            "description": "Task ID must match requested task ID"
        },
        "type": {
            "enum": ["manual", "automated"],
            "description": "Task type, if present, must match requested task type"
        },
        "issuer": {
            "type": "string",
            "minLength": 1,
            "description": "Action issuer, if present, must match value from the request"
        },
        "action": {
            "enum": ["prepare", "deactivate", "power-off", "reboot", "profile", "redeploy", "repair-link", "change-disk", "change-memory", "repair-bmc", "repair-overheat", "repair-capping"],
            "description": "Requested action, if present, must match value from the request"
        },
        "hosts": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "string",
                "minLength": 1
            },
            "description": "Hosts to process the action on, must match value from the request"
        },
        "comment": {
            "type": "string",
            "description": "optional comment from task's author"
        },
        "extra": {
            "type": "object",
            "description": "optional task parameters"
        },
        "status": {
            "enum": ["ok", "in-process", "rejected"],
            "description": "Current status of CMS task"
        },
        "message": {
            "type": "string",
            "description": "Message for the current status"
        },
    },
    "required": ["id", "hosts", "status"]
}

GET_RESPONSE = {
    "title": "Task as it was created by CMS",
    "description": "Wall-E checks task that were created earlier. If no task was found, CMS should return 404 NOT FOUND.",
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255,
            "description": "Task ID must match requested task ID"
        },
        "type": {
            "enum": ["manual", "automated"],
            "description": "Task type"
        },
        "issuer": {
            "type": "string",
            "minLength": 1,
            "description": "Action issuer"
        },
        "action": {
            "enum": ["prepare", "deactivate", "power-off", "reboot", "profile", "redeploy", "repair-link", "change-disk", "change-memory", "repair-bmc", "repair-overheat", "repair-capping"],
            "description": "Requested action"
        },
        "hosts": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "string",
                "minLength": 1
            },
            "description": "Hosts to process the action on"
        },
        "comment": {
            "type": "string",
            "description": "optional comment from task's author"
        },
        "extra": {
            "type": "object",
            "description": "optional task parameters"
        },
        "status": {
            "enum": ["ok", "in-process", "rejected"],
            "description": "Current status of CMS task"
        },
        "message": {
            "type": "string",
            "description": "Message for the current status"
        },
    },
    "required": ["id", "hosts", "status"]
}


GET_LIST_RESPONSE = {
    "title": "List of current tasks",
    "description": "Wall-E looks for staled tasks. CMS should return an object, containing a (possibly empty) list of tasks.",
    "type": "object",
    "properties": {
        "result": {
            "type": "array",
            "items": {
                "title": "Task as it was created by CMS",
                "type": "object",
                "properties": GET_RESPONSE['properties'],
            }
        }
    },
    "required": ["result"]
}


ERROR_RESPONSE = {
    "title": "Error message",
    "description": "In case of server errors (5xx) server should return JSON document of this shape.",
    "type": "object",
    "properties": {
        "message": {
            "type": "string",
            "description:": "Error message"
        }
    },
    "required": ["message"]
}
