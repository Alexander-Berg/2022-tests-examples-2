#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from sandbox import sdk2
import sandbox.common.types.task as ctt
import sandbox.projects.resource_types as resource_types
from sandbox.common.errors import TaskFailure


class TestPeopless(sdk2.Task):
    class Parameters(sdk2.Task.Parameters):
        wizard_config = sdk2.parameters.Resource("RA2 config for wizard check", resource_type=resource_types.REARRANGE_ACCEPTANCE_CONFIG, required=True)
        vertical_config = sdk2.parameters.Resource("RA2 config for vertical check", resource_type=resource_types.REARRANGE_ACCEPTANCE_CONFIG, required=True)
        desktop_queries = sdk2.parameters.Resource("Desktop queries for PPL", resource_type=resource_types.USERS_QUERIES, required=True)
        touch_queries = sdk2.parameters.Resource("Touch queries for PPL", resource_type=resource_types.USERS_QUERIES, required=True)
        beta_address_http_port = sdk2.parameters.String("Beta address (http port)", required=True)
        beta_address_apphost_port = sdk2.parameters.String("Beta address (apphost port)", required=True)

    def on_execute(self):
        with self.memoize_stage.stage1(commit_on_entrance=False):
            logging.info("Run RA2 tests")
            params = {
                "threads_count": 10,
                "unanswered_diff_threshold": 0.001,
                "unanswered_sources": "PEOPLE_SAAS:max_delta=0.01,PEOPLEP_SAAS:max_delta=0.01",
                "unanswered_tries_count": 5,
                "use_unanswered": True,
                "use_latest_parser_binary": True,
                "try_till_full_success": False,
                "beta_dump_all_json_1": False,
                "beta_dump_all_json_2": False,
                "beta_cgi_params_1": "&json_dump=searchdata.docs",
                "beta_cgi_params_2": "&json_dump=searchdata.docs&metahost2=PEOPLEP_SAAS:{}&srcrwr=PEOPLE_SAAS:{}".format(
                    self.Parameters.beta_address_http_port, self.Parameters.beta_address_apphost_port
                )
            }

            subtask_params = [
                {
                    "description": "Test wizard desktop",
                    "features_config": self.Parameters.wizard_config.id,
                    "req_resource_id": self.Parameters.desktop_queries.id,
                    "beta_collection_1": "search",
                    "beta_collection_2": "search"
                }, {
                    "description": "Test wizard touch",
                    "features_config": self.Parameters.wizard_config.id,
                    "req_resource_id": self.Parameters.touch_queries.id,
                    "beta_collection_1": "touchsearch",
                    "beta_collection_2": "touchsearch"
                }, {
                    "description": "Test vertical touch",
                    "features_config": self.Parameters.vertical_config.id,
                    "req_resource_id": self.Parameters.touch_queries.id,
                    "beta_collection_1": "touchpeople",
                    "beta_collection_2": "touchpeople"
                }, {
                    "description": "Test vertical desktop",
                    "features_config": self.Parameters.vertical_config.id,
                    "req_resource_id": self.Parameters.desktop_queries.id,
                    "beta_collection_1": "people",
                    "beta_collection_2": "people"
                }
            ]
            all_subtasks = []
            for subtask_param in subtask_params:
                params.update(subtask_param)
                subtask = sdk2.Task["REARRANGE_ACCEPTANCE_2"](
                    self, create_sub_task=True, **params)
                subtask.enqueue()
                all_subtasks.append(subtask.id)
            raise sdk2.WaitTask(all_subtasks, list(ctt.Status.Group.FINISH + ctt.Status.Group.BREAK), wait_all=True)
        with self.memoize_stage.stage2(commit_on_entrance=False):
            subtasks = self.find()
            if any(subtask.status != ctt.Status.SUCCESS for subtask in subtasks):
                for subtask in subtasks:
                    if subtask.status != ctt.Status.SUCCESS:
                        raise TaskFailure("Subtask {} finished with status {}".format(subtask.id, subtask.status))
            else:
                logging.info("Success testing!")
