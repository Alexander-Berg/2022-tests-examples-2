# -*- coding: utf-8 -*-
import logging
import json
import re
import requests

from sandbox import sdk2
import sandbox.common.types.task as ctt

TASK_ID_REGEXP = re.compile(r"TASK_ID_(?P<id>\d+)")


class AbtCalculationResult(sdk2.Resource):
    pass


class AbtCalculationExecutor(sdk2.Task):
    """ABT Calculation executor"""

    class Requirements(sdk2.Requirements):
        cores = 1
        ram = 8192

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 12 * 60 * 60

        key = sdk2.parameters.String(
            "Calculation key",
            description="Calcullation key",
            required=True,
            hint=True,
        )
        packet = sdk2.parameters.String(
            "Rem packet",
            description="Rem packet name",
        )
        author = sdk2.parameters.String(
            "Author"
        )
        restart = sdk2.parameters.Bool(
            "Restart",
            description="Need restart",
            default=False,
        )
        tasks = sdk2.parameters.JSON(
            "Ordered child tasks with context",
            description="List of task descriptions. If you need TASK ID of some task above in the list, use 'TASK_ID_{position in list}' (this task must be described before the current task)",
            required=True,
            default=[]
        )
        result_resource_type = sdk2.parameters.String(
            "Result resource type",
            description="Resource lookup runs from last to first task",
            required=True,
            default="ABT_CALCULATION_RESULT"
        )
        ems = sdk2.parameters.Bool(
            "Save to EMS",
            description="Need save to db",
            default=False,
        )
        with ems.value[True]:
            ems_url_template = sdk2.parameters.Url(
                "EMS API template",
                description="Use '{key}' and '{packet}' for insert their value",
                required=True
            )
            ems_headers = sdk2.parameters.JSON(
                "EMS headers"
            )
            ems_timeout = sdk2.parameters.Integer(
                "EMS timeout",
                required=True,
                default=120
            )
            ems_ttl = sdk2.parameters.Float(
                "TTL",
                description="TTL result in EMS databese"
            )

    class Context(sdk2.Task.Context):
        task_ids = []

    def generate_sub_task_input_parameters(self, task_description):
        logging.info("Generate input parameters for '{task_type}'".format(
            task_type=task_description["type"]
        ))
        input_parameters = {
            "key": self.Parameters.key
        }

        if not task_description.get("custom_fields"):
            logging.info("No custom fields")
            return input_parameters

        for field in task_description["custom_fields"]:
            logging.debug("Convert '{key}' field".format(key=field["key"]))
            value_text = json.dumps(field["value"])
            logging.debug("before: {before}".format(before=value_text))
            value_text = TASK_ID_REGEXP.sub(lambda m: str(self.Context.task_ids[int(m.group("id"))]), value_text)
            logging.debug("after : {after}".format(after=value_text))
            input_parameters[field["key"]] = json.loads(value_text)

        logging.info("End of generation of input_parameters for '{task_type}': '{input_parameters}".format(
            task_type=task_description["type"],
            input_parameters=input_parameters
        ))
        return input_parameters

    def on_execute(self):
        with self.memoize_stage.create_sub_tasks:
            logging.info("Get or create sub tasks")
            for task_description in self.Parameters.tasks:
                input_parameters = self.generate_sub_task_input_parameters(task_description)

                task_class = sdk2.Task[task_description["type"]]

                if not self.Parameters.restart:
                    logging.info("Find finished '{task_type}' task".format(
                        task_type=task_description["type"],
                    ))
                    task = sdk2.Task.find(
                        task_class,
                        input_parameters={
                            "key": self.Parameters.key
                        },
                        status=ctt.Status.Group.SUCCEED | ctt.Status.Group.EXECUTE | ctt.Status.Group.QUEUE
                    ).order(-sdk2.Task.id).first()

                    if task is not None:
                        logging.info("Found finished '{task_type}' task with id={task_id}".format(
                            task_type=task_description["type"],
                            task_id=task.id
                        ))
                        self.Context.task_ids.append(task.id)
                        continue

                logging.info("Create new '{task_type}' task".format(
                    task_type=task_description["type"],
                ))
                task = task_class(
                    self,
                    **input_parameters
                )
                self.Context.task_ids.append(task.id)

                logging.info("Update '{task_type}' task with id={task_id}".format(
                    task_type=task_description["type"],
                    task_id=task.id
                ))
                if "type" in task_description:
                    del task_description["type"]
                if "custom_fields" in task_description:
                    del task_description["custom_fields"]
                sdk2.Task.server.task[task.id].update(task_description)

                logging.info("Running '{task_type}' task with id={task_id}".format(
                    task_type=task.type,
                    task_id=task.id
                ))
                task.enqueue()

            logging.info("End getting or creating sub tasks")

        if self.id in self.Context.task_ids:
            raise Exception("Cycle")

        with self.memoize_stage.wait_sub_tasks:
            logging.info("Wait sub tasks")
            raise sdk2.WaitTask(
                self.Context.task_ids,
                ctt.Status.Group.FINISH | ctt.Status.Group.BREAK,
                wait_all=True,
            )

        result_resource_class = sdk2.Resource[self.Parameters.result_resource_type]
        result_resource = None  # last released resource
        for task_id in self.Context.task_ids:
            task = sdk2.Task[task_id]
            if task.status not in ctt.Status.Group.SUCCEED:
                raise Exception("Child '{task_type}' task with id={task_id} has status={task_status}".format(
                    task_type=task.type,
                    task_id=task.id,
                    task_status=task.status
                ))
            tmp_resource = sdk2.Resource.find(
                result_resource_class,
                task=task,
            ).first()
            if tmp_resource:
                result_resource = tmp_resource

        if result_resource is None:
            raise Exception("Resource '{resource_type}' not found".format(resource_type=self.Parameters.result_resource_type))

        result_data = sdk2.ResourceData(result_resource).path.read_bytes()
        if not result_data:
            raise Exception("Empty result data")

        if self.Parameters.ems:
            if self.Parameters.ems_ttl:
                logging.info("Append ttl to data")
                result_json = json.loads(result_data)
                result_json["ttl"] = self.Parameters.ems_ttl
                result_data = json.dumps(result_json)
                logging.info("Appended ttl to data")

            logging.info("Save data to ems")
            requests.post(
                self.Parameters.ems_url_template.format(
                    key=self.Parameters.key,
                    packet=self.Parameters.packet,
                ),
                data=result_data,
                headers=self.Parameters.ems_headers,
                timeout=self.Parameters.ems_timeout,
            ).raise_for_status()
            logging.info("Data has been saved")

        logging.info("End")
