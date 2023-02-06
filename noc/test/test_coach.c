/*
 * FreeSWITCH Modular Media Switching Software Library / Soft-Switch Application
 * Copyright (C) 2005-2020, Anthony Minessale II <anthm@freeswitch.org>
 *
 * Version: MPL 1.1
 *
 * The contents of this file are subject to the Mozilla Public License Version
 * 1.1 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 * http://www.mozilla.org/MPL/
 *
 * Software distributed under the License is distributed on an "AS IS" basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
 * for the specific language governing rights and limitations under the
 * License.
 *
 * The Original Code is FreeSWITCH Modular Media Switching Software Library / Soft-Switch Application
 *
 * The Initial Developer of the Original Code is
 * Anthony Minessale II <anthm@freeswitch.org>
 * Portions created by the Initial Developer are Copyright (C)
 * the Initial Developer. All Rights Reserved.
 *
 * Contributor(s):
 * Chris Rienzo <chris@signalwire.com>
 *
 *
 * test_coach.c -- test member coaching API
 *
 */
#include <switch.h>
#include <stdlib.h>
#include <mod_conference.h>

#include <test/switch_test.h>

static cJSON *get_member(cJSON *dump, const char *member_uuid)
{
	cJSON *members = cJSON_GetObjectItem(dump, "members");
	cJSON *member = NULL;
	if (!members) {
		return NULL;
	}
	for (member = members->child; member; member = member->next) {
		if (!strcmp(switch_str_nil(cJSON_GetObjectCstr(member, "uuid")), member_uuid)) {
			return member;
		}
	}
	return NULL;
}

static cJSON *json_list_local_conference(const char *conf_id)
{
	switch_stream_handle_t stream;
	cJSON *conference = NULL;
	cJSON *conferences = NULL;
	char *args = switch_mprintf("%s json_list", conf_id);
	SWITCH_STANDARD_STREAM(stream);

	switch_api_execute("conference", args, NULL, &stream);
	switch_safe_free(args);
	if (!strncmp(stream.data, "-ERR", 4)) {
		switch_safe_free(stream.data);
		return NULL;
	}
	conferences = cJSON_Parse((char *)stream.data);
	if (conferences) {
		char *txt;
		conference = cJSON_DetachItemFromArray(conferences, 0);
		txt = cJSON_Print(conference);
		switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_NOTICE, "Conference \"%s\"\n%s\n", conf_id, txt);
		switch_safe_free(txt);
		cJSON_Delete(conferences);
	}
	switch_safe_free(stream.data);
	return conference;
}

static switch_core_session_t *new_member_session(void)
{
	switch_event_t *vars = NULL;
	switch_core_session_t *session = NULL;
	switch_call_cause_t cause;
	switch_event_create_plain(&vars, SWITCH_EVENT_CHANNEL_DATA);
	switch_event_add_header_string(vars, SWITCH_STACK_BOTTOM, "origination_caller_id_number", "+15551112222");
	switch_event_add_header(vars, SWITCH_STACK_BOTTOM, "rate", "%d", 8000);
	switch_ivr_originate(NULL, &session, &cause, "null/+15553334444", 2, NULL, NULL, NULL, NULL, vars, SOF_NONE, NULL, NULL);
	if (session) {
		switch_channel_t *channel = switch_core_session_get_channel(session);
		switch_channel_set_state(channel, CS_SOFT_EXECUTE);
		switch_channel_wait_for_state(channel, NULL, CS_SOFT_EXECUTE);
		switch_channel_set_variable(channel, "send_silence_when_idle", "-1");
		fst_session_park(session);
		switch_channel_wait_for_state(channel, NULL, CS_PARK);
	}
	switch_event_destroy(&vars);
	return session;
}

static char *exec_conference_api(const char *conference_name, const char *sub_cmd, const char *args)
{
	switch_stream_handle_t stream;
	char *cmd_args = switch_mprintf("%s %s %s", conference_name, sub_cmd, args);
	SWITCH_STANDARD_STREAM(stream);
	switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "API request: conference %s\n", cmd_args);
	switch_api_execute("conference", cmd_args, NULL, &stream);
	switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "API reply: %s\n", (char *)stream.data);
	switch_safe_free(cmd_args);
	return stream.data;
}

/* verify members can (or can't) hear audio played */
static switch_status_t verify_audio_path(switch_core_session_t *source, switch_core_session_t *target_1, switch_bool_t target_1_can_hear, switch_core_session_t *target_2, switch_bool_t target_2_can_hear)
{
	switch_event_t *recording_args = NULL;
	switch_bool_t result = SWITCH_TRUE;
	char recording_uuid[SWITCH_UUID_FORMATTED_LENGTH + 1] = { 0 };
	const char *source_recording = NULL;
	const char *target_1_recording = NULL;
	const char *target_2_recording = NULL;

	// set up session recording to detect silence
	switch_event_create(&recording_args, SWITCH_EVENT_CLONE);
	switch_event_add_header_string(recording_args, SWITCH_STACK_BOTTOM, "RECORD_WRITE_ONLY", "true");
	switch_event_add_header_string(recording_args, SWITCH_STACK_BOTTOM, "RECORD_MIN_SEC", "1");
	switch_event_add_header_string(recording_args, SWITCH_STACK_BOTTOM, "RECORD_INITIAL_TIMEOUT_MS", "1000");

	switch_uuid_str(recording_uuid, sizeof(recording_uuid));

	source_recording = switch_core_session_sprintf(source, "%s" SWITCH_PATH_SEPARATOR "%s-source.wav", SWITCH_GLOBAL_dirs.temp_dir, recording_uuid);
	if (switch_ivr_record_session_event(source, source_recording, 0, NULL, recording_args) != SWITCH_STATUS_SUCCESS) {
		switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(source), SWITCH_LOG_ERROR, "Failed to start recording %s\n", switch_channel_get_name(switch_core_session_get_channel(source)));
		switch_event_destroy(&recording_args);
		return SWITCH_STATUS_NOT_INITALIZED;
	}

	target_1_recording = switch_core_session_sprintf(target_1, "%s" SWITCH_PATH_SEPARATOR "%s-target-1.wav", SWITCH_GLOBAL_dirs.temp_dir, recording_uuid);
	if (switch_ivr_record_session_event(target_1, target_1_recording, 0, NULL, recording_args) != SWITCH_STATUS_SUCCESS) {
		switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(source), SWITCH_LOG_ERROR, "Failed to start recording %s\n", switch_channel_get_name(switch_core_session_get_channel(target_1)));
		switch_ivr_stop_record_session(source, source_recording);
		unlink(source_recording);
		switch_event_destroy(&recording_args);
		return SWITCH_STATUS_NOT_INITALIZED;
	}

	if (target_2) {
		target_2_recording = switch_core_session_sprintf(target_2, "%s" SWITCH_PATH_SEPARATOR "%s-target-2.wav", SWITCH_GLOBAL_dirs.temp_dir, recording_uuid);
		if (switch_ivr_record_session_event(target_2, target_2_recording, 0, NULL, recording_args) != SWITCH_STATUS_SUCCESS) {
			switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(source), SWITCH_LOG_ERROR, "Failed to start recording %s\n", switch_channel_get_name(switch_core_session_get_channel(target_2)));
			switch_ivr_stop_record_session(source, source_recording);
			unlink(source_recording);
			switch_ivr_stop_record_session(target_1, target_1_recording);
			unlink(target_1_recording);
			switch_event_destroy(&recording_args);
			return SWITCH_STATUS_NOT_INITALIZED;
		}
	}

	// Play audio to source
	switch_ivr_displace_session(source, "tone_stream://%(1500,100,800)", 0, "mrf");

	// wait for recording timeouts
	switch_sleep(1000 * 2000);

	switch_ivr_stop_record_session(source, source_recording);
	switch_ivr_stop_record_session(target_1, target_1_recording);
	if (target_2) {
		switch_ivr_stop_record_session(target_2, target_2_recording);
	}
	switch_sleep(1000 * 1000);

	switch_ivr_stop_displace_session(source, "tone_stream://%(1500,100,800)");

	if (switch_file_exists(source_recording, switch_core_session_get_pool(source)) == SWITCH_STATUS_SUCCESS) {
		switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(source), SWITCH_LOG_INFO, "(source) %s heard something, FAIL\n", switch_channel_get_name(switch_core_session_get_channel(source)));
		result = SWITCH_FALSE;
	} else {
		switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(source), SWITCH_LOG_INFO, "(source) %s heard nothing, PASS\n", switch_channel_get_name(switch_core_session_get_channel(source)));
		result = SWITCH_TRUE;
	}

	unlink(source_recording);

	if (switch_file_exists(target_1_recording, switch_core_session_get_pool(target_1)) == SWITCH_STATUS_SUCCESS) {
		switch_bool_t pass = target_1_can_hear;
		switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(source), SWITCH_LOG_INFO, "(target 1) %s heard something, %s\n", switch_channel_get_name(switch_core_session_get_channel(target_1)), pass ? "PASS" : "FAIL");
		result = result && pass;
	} else {
		switch_bool_t pass = !target_1_can_hear;
		switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(source), SWITCH_LOG_INFO, "(target 1) %s heard nothing, %s\n", switch_channel_get_name(switch_core_session_get_channel(target_1)), pass ? "PASS" : "FAIL");
		result = result && pass;
	}
	unlink(target_1_recording);

	if (target_2) {
		if (switch_file_exists(target_2_recording, switch_core_session_get_pool(target_2)) == SWITCH_STATUS_SUCCESS) {
			switch_bool_t pass = target_2_can_hear;
			switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(source), SWITCH_LOG_INFO, "(target 2) %s heard something, %s\n", switch_channel_get_name(switch_core_session_get_channel(target_2)), pass ? "PASS" : "FAIL");
			result = result && pass;
		} else {
			switch_bool_t pass = !target_2_can_hear;
			switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(source), SWITCH_LOG_INFO, "(target 2) %s heard nothing, %s\n", switch_channel_get_name(switch_core_session_get_channel(target_2)), pass ? "PASS" : "FAIL");
			result = result && pass;
		}
		unlink(target_2_recording);
	}

	switch_event_destroy(&recording_args);

	return result ? SWITCH_STATUS_SUCCESS : SWITCH_STATUS_FALSE;
}

FST_CORE_BEGIN("./conf")
{
	FST_SUITE_BEGIN(member_coaching)
	{
		FST_SETUP_BEGIN()
		{
		}
		FST_SETUP_END()

		FST_TEARDOWN_BEGIN()
		{
			switch_core_session_hupall(SWITCH_CAUSE_NORMAL_CLEARING);
		}
		FST_TEARDOWN_END()

		/* Test conference APP acceptance of JSON args */
		FST_SESSION_BEGIN(json_args_test)
		{
			const char *member_uuid = switch_core_session_get_uuid(fst_session);
			const char *conference_name = member_uuid;
			cJSON *conference;
			cJSON *member;
			cJSON *args = cJSON_CreateObject();
			char *args_str = NULL;
			cJSON_AddStringToObject(args, "name", conference_name);
			cJSON_AddStringToObject(args, "profile", "default");
			cJSON_AddStringToObject(args, "pin", "12345");
			cJSON_AddStringToObject(args, "flags", "mute|deaf");
			cJSON_AddStringToObject(args, "bridge", "null/12345");
			args_str = cJSON_PrintUnformatted(args);
			cJSON_Delete(args);

			fst_session_park(fst_session);

			switch_sleep(1000 * 3000);

			// create a new conference with json args
			switch_core_session_execute_application_async(fst_session, "conference", args_str);
			switch_safe_free(args_str);
			switch_sleep(1000 * 3000);

			// check initial member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "can_speak")), "Expect member not able to speak");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "can_hear")), "Expect member not able to hear");
			cJSON_Delete(conference);
		}
		FST_SESSION_END()

		/* Test modifying member coaching with the coach and coach-stop APIs */
		FST_SESSION_BEGIN(coach_api_test)
		{
			const char *member_uuid = switch_core_session_get_uuid(fst_session);
			switch_core_session_t *fst_session_2 = NULL;
			const char *member_uuid_2 = NULL;
			switch_core_session_t *fst_session_3 = NULL;
			const char *member_uuid_3 = NULL;
			const char *conference_name = member_uuid;
			cJSON *conference;
			cJSON *member;
			char *api_reply = NULL;

			fst_session_park(fst_session);
			switch_channel_set_name(switch_core_session_get_channel(fst_session), "member-1");

			// create a new conference
			switch_core_session_execute_application_async(fst_session, "conference", conference_name);
			switch_sleep(1000 * 3000);

			// check initial member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			// add a member to the conference
			fst_session_2 = new_member_session();
			switch_channel_set_name(switch_core_session_get_channel(fst_session_2), "member-2");
			member_uuid_2 = switch_core_session_get_uuid(fst_session_2);
			switch_core_session_execute_application_async(fst_session_2, "conference", conference_name);
			switch_sleep(1000 * 3000);

			// check second member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 2 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 2 not to be a target of coaching");
			cJSON_Delete(conference);

			// add a coach for the initial member using the API
			fst_session_3 = new_member_session();
			switch_channel_set_name(switch_core_session_get_channel(fst_session_3), "member-3");
			member_uuid_3 = switch_core_session_get_uuid(fst_session_3);
			switch_core_session_execute_application_async(fst_session_3, "conference", conference_name);
			switch_sleep(1000 * 3000);


			api_reply = exec_conference_api(conference_name, "coach", switch_core_sprintf(fst_pool, "uuid=%s uuid=%s", member_uuid_3, member_uuid));
			fst_xcheck(api_reply != NULL && !strncmp("+OK ", api_reply, strlen("+OK ")), "Expect coach API to reply +OK");
			switch_safe_free(api_reply);

			// check coach member and coach target member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid_3);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 3 to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 3 not to be a target of coaching");
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 2 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 2 not to be a target of coaching");
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 to be a target of coaching");
			cJSON_Delete(conference);

			switch_channel_set_name(switch_core_session_get_channel(fst_session), "member-1-target");
			switch_channel_set_name(switch_core_session_get_channel(fst_session_3), "member-3-coach");
			fst_xcheck(verify_audio_path(fst_session, fst_session_2, SWITCH_TRUE, fst_session_3, SWITCH_TRUE) == SWITCH_STATUS_SUCCESS, "Expect members 2 and 3 can hear member 1");
			fst_xcheck(verify_audio_path(fst_session_2, fst_session, SWITCH_TRUE, fst_session_3, SWITCH_TRUE) == SWITCH_STATUS_SUCCESS, "Expect members 1 and 3 can hear member 2");
			fst_xcheck(verify_audio_path(fst_session_3, fst_session, SWITCH_TRUE, fst_session_2, SWITCH_FALSE) == SWITCH_STATUS_SUCCESS, "Expect only member 1 can hear member 3");
			switch_channel_set_name(switch_core_session_get_channel(fst_session), "member-1");
			switch_channel_set_name(switch_core_session_get_channel(fst_session_3), "member-3");

			// attempt to coach duplicate member - this should be a no-op
			api_reply = exec_conference_api(conference_name, "coach", switch_core_sprintf(fst_pool, "uuid=%s uuid=%s", member_uuid_3, member_uuid));
			fst_xcheck(api_reply != NULL && !strncmp("+OK ", api_reply, strlen("+OK ")), "Expect coach API to reply +OK");
			switch_safe_free(api_reply);
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid_3);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 3 to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 3 not to be a target of coaching");
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 2 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 2 not to be a target of coaching");
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 to be a target of coaching");
			cJSON_Delete(conference);

			// attempt to coach a second member - this replace the first member as a coach target
			api_reply = exec_conference_api(conference_name, "coach", switch_core_sprintf(fst_pool, "uuid=%s uuid=%s", member_uuid_3, member_uuid_2));
			fst_xcheck(api_reply != NULL && !strncmp("+OK ", api_reply, strlen("+OK ")), "Expect coach API to reply +OK");
			switch_safe_free(api_reply);
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid_3);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 3 to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 3 not to be a target of coaching");
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 2 not to be coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 2 to be a target of coaching");
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			switch_channel_set_name(switch_core_session_get_channel(fst_session_2), "member-2-target");
			switch_channel_set_name(switch_core_session_get_channel(fst_session_3), "member-3-coach");
			fst_xcheck(verify_audio_path(fst_session, fst_session_2, SWITCH_TRUE, fst_session_3, SWITCH_TRUE) == SWITCH_STATUS_SUCCESS, "Expect members 2 and 3 can hear member 1");
			fst_xcheck(verify_audio_path(fst_session_2, fst_session, SWITCH_TRUE, fst_session_3, SWITCH_TRUE) == SWITCH_STATUS_SUCCESS, "Expect members 1 and 3 can hear member 2");
			fst_xcheck(verify_audio_path(fst_session_3, fst_session, SWITCH_FALSE, fst_session_2, SWITCH_TRUE) == SWITCH_STATUS_SUCCESS, "Expect only member 2 can hear member 3");
			switch_channel_set_name(switch_core_session_get_channel(fst_session_2), "member-2");
			switch_channel_set_name(switch_core_session_get_channel(fst_session_3), "member-3");

			// stop coaching when coaching
			api_reply = exec_conference_api(conference_name, "coach-stop", switch_core_sprintf(fst_pool, "uuid=%s", member_uuid_3));
			fst_xcheck(api_reply != NULL && !strncmp("+OK ", api_reply, strlen("+OK ")), "Expect coach-stop API to reply +OK");
			switch_safe_free(api_reply);
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid_3);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 3 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 3 not to be a target of coaching");
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 2 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 2 not to be a target of coaching");
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			fst_xcheck(verify_audio_path(fst_session, fst_session_2, SWITCH_TRUE, fst_session_3, SWITCH_TRUE) == SWITCH_STATUS_SUCCESS, "Expect members 2 and 3 can hear member 1");
			fst_xcheck(verify_audio_path(fst_session_2, fst_session, SWITCH_TRUE, fst_session_3, SWITCH_TRUE) == SWITCH_STATUS_SUCCESS, "Expect members 1 and 3 can hear member 2");
			fst_xcheck(verify_audio_path(fst_session_3, fst_session, SWITCH_TRUE, fst_session_2, SWITCH_TRUE) == SWITCH_STATUS_SUCCESS, "Expect members 1 and 2 can hear member 3");

			// stop coaching when not coaching - no-op
			api_reply = exec_conference_api(conference_name, "coach-stop", switch_core_sprintf(fst_pool, "uuid=%s", member_uuid_3));
			fst_xcheck(api_reply != NULL && !strncmp("+OK ", api_reply, strlen("+OK ")), "Expect coach-stop API to reply +OK");
			switch_safe_free(api_reply);
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid_3);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 3 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 3 not to be a target of coaching");
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 2 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 2 not to be a target of coaching");
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			// attempt to coach a non-existant member
			api_reply = exec_conference_api(conference_name, "coach", switch_core_sprintf(fst_pool, "uuid=%s uuid=not-a-valid-uuid", member_uuid_3));
			fst_xcheck(api_reply != NULL && !strncmp("-ERR ", api_reply, strlen("-ERR ")), "Expect coach API to reply -ERR");
			switch_safe_free(api_reply);
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid_3);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 3 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 3 not to be a target of coaching");
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 2 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 2 not to be a target of coaching");
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			// start coaching member 2 again
			api_reply = exec_conference_api(conference_name, "coach", switch_core_sprintf(fst_pool, "uuid=%s uuid=%s", member_uuid_3, member_uuid_2));
			fst_xcheck(api_reply != NULL && !strncmp("+OK ", api_reply, strlen("+OK ")), "Expect coach API to reply +OK");
			switch_safe_free(api_reply);
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid_3);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 3 to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 3 not to be a target of coaching");
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 2 not to be coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 2 to be a target of coaching");
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			switch_channel_set_name(switch_core_session_get_channel(fst_session_2), "member-2-target");
			switch_channel_set_name(switch_core_session_get_channel(fst_session_3), "member-3-coach");
			fst_xcheck(verify_audio_path(fst_session, fst_session_2, SWITCH_TRUE, fst_session_3, SWITCH_TRUE) == SWITCH_STATUS_SUCCESS, "Expect members 2 and 3 can hear member 1");
			fst_xcheck(verify_audio_path(fst_session_2, fst_session, SWITCH_TRUE, fst_session_3, SWITCH_TRUE) == SWITCH_STATUS_SUCCESS, "Expect members 1 and 3 can hear member 2");
			fst_xcheck(verify_audio_path(fst_session_3, fst_session, SWITCH_FALSE, fst_session_2, SWITCH_TRUE) == SWITCH_STATUS_SUCCESS, "Expect only member 2 can hear member 3");
			switch_channel_set_name(switch_core_session_get_channel(fst_session_2), "member-2");
			switch_channel_set_name(switch_core_session_get_channel(fst_session_3), "member-3");
			// hang up coached member- this should kick the coach from the conference
			switch_channel_hangup(switch_core_session_get_channel(fst_session_2), SWITCH_CAUSE_NORMAL_CLEARING);
			switch_core_session_rwunlock(fst_session_2);

			switch_sleep(1000 * 1000);
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid_3);
			fst_xcheck(member == NULL, "Expect member 3 to be gone");
			member = get_member(conference, member_uuid_2);
			fst_xcheck(member == NULL, "Expect member 2 to be gone");
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			switch_channel_hangup(switch_core_session_get_channel(fst_session_3), SWITCH_CAUSE_NORMAL_CLEARING);
			switch_core_session_rwunlock(fst_session_3);
		}
		FST_SESSION_END()

		/* Test joining a conference to coach a member in the conference APP */
		FST_SESSION_BEGIN(coach_app_test)
		{
			const char *member_uuid = switch_core_session_get_uuid(fst_session);
			switch_core_session_t *fst_session_2 = NULL;
			const char *member_uuid_2 = NULL;
			const char *conference_name = member_uuid;
			cJSON *conference;
			cJSON *member;
			cJSON *app_args = NULL;
			char *args = NULL;

			fst_session_park(fst_session);

			// create a new conference
			switch_core_session_execute_application_async(fst_session, "conference", conference_name);
			switch_sleep(1000 * 3000);

			// check initial member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			// add a member to the conference coaching the first member
			fst_session_2 = new_member_session();
			member_uuid_2 = switch_core_session_get_uuid(fst_session_2);
			app_args = cJSON_CreateObject();
			cJSON_AddStringToObject(app_args, "name", conference_name);
			cJSON_AddStringToObject(app_args, "coach", switch_core_sprintf(fst_pool, "uuid=%s", member_uuid));
			args = cJSON_PrintUnformatted(app_args);
			switch_core_session_execute_application_async(fst_session_2, "conference", args);
			switch_safe_free(args);
			cJSON_Delete(app_args);
			switch_sleep(1000 * 3000);

			// check second member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 2 to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 2 not to be a target of coaching");
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 to be a target of coaching");
			cJSON_Delete(conference);

			switch_channel_set_name(switch_core_session_get_channel(fst_session), "member-1");
			switch_channel_set_name(switch_core_session_get_channel(fst_session_2), "member-2");
			fst_xcheck(verify_audio_path(fst_session, fst_session_2, SWITCH_TRUE, NULL, SWITCH_FALSE) == SWITCH_STATUS_SUCCESS, "Expect member 2 can hear member 1");
			fst_xcheck(verify_audio_path(fst_session_2, fst_session, SWITCH_TRUE, NULL, SWITCH_FALSE) == SWITCH_STATUS_SUCCESS, "Expect member 1 can hear member 2");

			// hang up coached member- this should kick the coach from the conference
			switch_channel_hangup(switch_core_session_get_channel(fst_session), SWITCH_CAUSE_NORMAL_CLEARING);

			switch_sleep(1000 * 1000);
			conference = json_list_local_conference(conference_name);
			fst_xcheck(conference == NULL, "Expect conference to be gone");
			cJSON_Delete(conference);

			switch_channel_hangup(switch_core_session_get_channel(fst_session_2), SWITCH_CAUSE_NORMAL_CLEARING);
			switch_core_session_rwunlock(fst_session_2);
		}
		FST_SESSION_END()

		/* Test conference APP attempting to coach when pass a bad param */
		FST_SESSION_BEGIN(coach_app_error_test)
		{
			const char *member_uuid = switch_core_session_get_uuid(fst_session);
			switch_core_session_t *fst_session_2 = NULL;
			const char *member_uuid_2 = NULL;
			const char *conference_name = member_uuid;
			cJSON *conference;
			cJSON *member;
			cJSON *app_args = NULL;
			char *args = NULL;
			char *api_reply = NULL;

			fst_session_park(fst_session);

			// create a new conference
			switch_core_session_execute_application_async(fst_session, "conference", conference_name);
			switch_sleep(1000 * 3000);

			// check initial member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			// Add a new member that attempts to coach a member that doesn't exist
			fst_session_2 = new_member_session();
			member_uuid_2 = switch_core_session_get_uuid(fst_session_2);
			app_args = cJSON_CreateObject();
			cJSON_AddStringToObject(app_args, "name", conference_name);
			cJSON_AddStringToObject(app_args, "coach", "bad-uuid");
			args = cJSON_PrintUnformatted(app_args);
			switch_core_session_execute_application_async(fst_session_2, "conference", args);
			switch_safe_free(args);
			cJSON_Delete(app_args);
			switch_sleep(1000 * 3000);

			// check member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid_2);
			fst_xcheck(member == NULL, "Expect member 2 to be gone");
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			// First member attempts to coach member that is not in the conference
			api_reply = exec_conference_api(conference_name, "coach", switch_core_sprintf(fst_pool, "uuid=%s uuid=%s", member_uuid, member_uuid_2));
			fst_xcheck(api_reply != NULL && !strncmp("-ERR ", api_reply, strlen("-ERR ")), "Expect coach API to reply -ERR");
			switch_safe_free(api_reply);
			switch_sleep(1000 * 1000);

			// check member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid_2);
			fst_xcheck(member == NULL, "Expect member 2 to be gone");
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			// hang up the first member- this will end the conference
			switch_channel_hangup(switch_core_session_get_channel(fst_session), SWITCH_CAUSE_NORMAL_CLEARING);

			switch_sleep(1000 * 1000);
			conference = json_list_local_conference(conference_name);
			fst_xcheck(conference == NULL, "Expect conference to be gone");
			cJSON_Delete(conference);

			switch_channel_hangup(switch_core_session_get_channel(fst_session_2), SWITCH_CAUSE_NORMAL_CLEARING);
			switch_core_session_rwunlock(fst_session_2);
		}
		FST_SESSION_END()

		/* Test coach_bridge set in conference APP */
		FST_SESSION_BEGIN(coach_bridge_app_test)
		{
			const char *member_uuid = switch_core_session_get_uuid(fst_session);
			switch_core_session_t *fst_session_2 = NULL;
			const char *member_uuid_2 = NULL;
			const char *conference_name = member_uuid;
			cJSON *conference;
			cJSON *member;
			cJSON *app_args = NULL;
			char *args = NULL;

			fst_session_park(fst_session);

			// create a new conference coaching outbound call
			app_args = cJSON_CreateObject();
			cJSON_AddStringToObject(app_args, "name", conference_name);
			cJSON_AddStringToObject(app_args, "coach_bridge", "{origination_external_id=coach-bridge}null/coach-bridge");
			args = cJSON_PrintUnformatted(app_args);
			switch_core_session_execute_application_async(fst_session, "conference", args);
			switch_safe_free(args);
			cJSON_Delete(app_args);
			switch_sleep(1000 * 3000);

			fst_session_2 = switch_core_session_locate("coach-bridge");
			fst_requires(fst_session_2 != NULL);
			member_uuid_2 = switch_core_session_get_uuid(fst_session_2);

			// check member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member not to be a target of coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_bridge")), "Expect member to be coaching a bridge");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_bridge_target")), "Expect member not to be the coached bridge");
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect coached bridge not to be coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect coached bridge to be a target of coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_bridge")), "Expect coached bridge not to be coaching a bridge");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_bridge_target")), "Expect coached bridge to be the coached bridge");
			cJSON_Delete(conference);

			switch_channel_set_name(switch_core_session_get_channel(fst_session), "member-1-");
			switch_channel_set_name(switch_core_session_get_channel(fst_session_2), "member-2-bridge");

			fst_xcheck(verify_audio_path(fst_session, fst_session_2, SWITCH_TRUE, NULL, SWITCH_FALSE) == SWITCH_STATUS_SUCCESS, "Expect coached bridge can hear member");
			fst_xcheck(verify_audio_path(fst_session_2, fst_session, SWITCH_TRUE, NULL, SWITCH_FALSE) == SWITCH_STATUS_SUCCESS, "Expect member can hear coached bridge");

			// hang up coaching member- this should kick the bridge from the conference
			switch_channel_hangup(switch_core_session_get_channel(fst_session), SWITCH_CAUSE_NORMAL_CLEARING);

			switch_sleep(1000 * 1000);
			conference = json_list_local_conference(conference_name);
			fst_xcheck(conference == NULL, "Expect conference to be gone");
			cJSON_Delete(conference);

			switch_channel_hangup(switch_core_session_get_channel(fst_session_2), SWITCH_CAUSE_NORMAL_CLEARING);
			switch_core_session_rwunlock(fst_session_2);
		}
		FST_SESSION_END()

		/* Test coach_bridge set in conference APP as serialized dial handle */
		FST_SESSION_BEGIN(coach_bridge_json_app_test)
		{
			const char *member_uuid = switch_core_session_get_uuid(fst_session);
			switch_core_session_t *fst_session_2 = NULL;
			const char *member_uuid_2 = NULL;
			const char *conference_name = member_uuid;
			cJSON *conference;
			cJSON *member;
			cJSON *app_args = NULL;
			char *args = NULL;
			switch_dial_handle_t *dh = NULL;
			switch_dial_leg_list_t *ll = NULL;
			switch_dial_leg_t *leg = NULL;
			char *coach_bridge_json_str = NULL;

			fst_session_park(fst_session);

			// create a new conference coaching outbound call using a serialized dial handle
			app_args = cJSON_CreateObject();
			cJSON_AddStringToObject(app_args, "name", conference_name);
			switch_dial_handle_create(&dh);
			switch_dial_handle_add_leg_list(dh, &ll);
			switch_dial_leg_list_add_leg(ll, &leg, "null/coach-bridge");
			switch_dial_handle_add_leg_var(leg, "origination_external_id", "coach-bridge");
			switch_dial_handle_serialize_json(dh, &coach_bridge_json_str);
			cJSON_AddStringToObject(app_args, "coach_bridge", coach_bridge_json_str);
			switch_safe_free(coach_bridge_json_str);
			switch_dial_handle_destroy(&dh);
			args = cJSON_PrintUnformatted(app_args);
			switch_core_session_execute_application_async(fst_session, "conference", args);
			switch_safe_free(args);
			cJSON_Delete(app_args);
			switch_sleep(1000 * 3000);

			fst_session_2 = switch_core_session_locate("coach-bridge");
			fst_requires(fst_session_2 != NULL);
			member_uuid_2 = switch_core_session_get_uuid(fst_session_2);

			// check member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect coach bridge not to be coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect coach bridge to be a target of coaching");
			cJSON_Delete(conference);

			switch_channel_set_name(switch_core_session_get_channel(fst_session), "member-1");
			switch_channel_set_name(switch_core_session_get_channel(fst_session_2), "member-2");
			fst_xcheck(verify_audio_path(fst_session, fst_session_2, SWITCH_TRUE, NULL, SWITCH_FALSE) == SWITCH_STATUS_SUCCESS, "Expect member 2 can hear member 1");
			fst_xcheck(verify_audio_path(fst_session_2, fst_session, SWITCH_TRUE, NULL, SWITCH_FALSE) == SWITCH_STATUS_SUCCESS, "Expect member 1 can hear member 2");

			// hang up coaching member- this should kick the bridge from the conference
			switch_channel_hangup(switch_core_session_get_channel(fst_session), SWITCH_CAUSE_NORMAL_CLEARING);

			switch_sleep(1000 * 1000);
			conference = json_list_local_conference(conference_name);
			fst_xcheck(conference == NULL, "Expect conference to be gone");
			cJSON_Delete(conference);

			switch_channel_hangup(switch_core_session_get_channel(fst_session_2), SWITCH_CAUSE_NORMAL_CLEARING);
			switch_core_session_rwunlock(fst_session_2);
		}
		FST_SESSION_END()

		/* Test failure to dial coach_bridge in conference APP */
		FST_SESSION_BEGIN(coach_bridge_app_error_test)
		{
			const char *member_uuid = switch_core_session_get_uuid(fst_session);
			const char *conference_name = member_uuid;
			cJSON *app_args = NULL;
			cJSON *conference = NULL;
			char *args = NULL;

			fst_session_park(fst_session);

			// create a new conference coaching outbound call that is not answered
			app_args = cJSON_CreateObject();
			cJSON_AddStringToObject(app_args, "name", conference_name);
			cJSON_AddStringToObject(app_args, "coach_bridge", "{origination_external_id=coach-bridge}error/user_busy");
			args = cJSON_PrintUnformatted(app_args);
			switch_core_session_execute_application_async(fst_session, "conference", args);
			switch_safe_free(args);
			cJSON_Delete(app_args);
			switch_sleep(1000 * 3000);

			// check member flags
			conference = json_list_local_conference(conference_name);
			fst_xcheck(conference == NULL, "Expect conference to be gone");
			cJSON_Delete(conference);
		}
		FST_SESSION_END()

		/* Hang up a coach bridge channel created by conference APP */
		FST_SESSION_BEGIN(coach_bridge_hangup_test)
		{
			const char *member_uuid = switch_core_session_get_uuid(fst_session);
			switch_core_session_t *fst_session_2 = NULL;
			const char *member_uuid_2 = NULL;
			const char *conference_name = member_uuid;
			cJSON *conference;
			cJSON *member;
			cJSON *app_args = NULL;
			char *args = NULL;

			fst_session_park(fst_session);

			// create a new conference coaching outbound call
			app_args = cJSON_CreateObject();
			cJSON_AddStringToObject(app_args, "name", conference_name);
			cJSON_AddStringToObject(app_args, "coach_bridge", "{origination_external_id=coach-bridge-hangup}null/coach-bridge-hangup");
			args = cJSON_PrintUnformatted(app_args);
			switch_core_session_execute_application_async(fst_session, "conference", args);
			switch_safe_free(args);
			cJSON_Delete(app_args);
			switch_sleep(1000 * 3000);

			fst_session_2 = switch_core_session_locate("coach-bridge-hangup");
			fst_requires(fst_session_2 != NULL);
			member_uuid_2 = switch_core_session_get_uuid(fst_session_2);

			// check member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect coach bridge not to be coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect coach bridge to be a target of coaching");
			cJSON_Delete(conference);

			// hang up bridge member- this should kick the coach from the conference
			switch_channel_hangup(switch_core_session_get_channel(fst_session_2), SWITCH_CAUSE_NORMAL_CLEARING);

			switch_sleep(1000 * 1000);
			conference = json_list_local_conference(conference_name);
			fst_xcheck(conference == NULL, "Expect conference to be gone");
			cJSON_Delete(conference);

			switch_core_session_rwunlock(fst_session_2);
		}
		FST_SESSION_END()

		/* Join an existing conference w/ coach_bridge set in JSON app args */
		FST_SESSION_BEGIN(coach_bridge_running_test)
		{
			switch_core_session_t *member_session = fst_session;
			const char *member_uuid = switch_core_session_get_uuid(fst_session);
			switch_core_session_t *coach_bridge_session = NULL;
			const char *coach_bridge_uuid = NULL;
			switch_core_session_t *coach_bridge_target_session = NULL;
			const char *coach_bridge_target_uuid = NULL;
			const char *conference_name = member_uuid;
			cJSON *conference;
			cJSON *member;
			cJSON *app_args = NULL;
			char *args = NULL;

			fst_session_park(member_session);
			switch_channel_set_name(switch_core_session_get_channel(member_session), "member");

			// create a new conference
			switch_core_session_execute_application_async(member_session, "conference", member_uuid);
			switch_sleep(1000 * 3000);

			// Add a 2nd member to the running conference, coaching an outbound call
			coach_bridge_session = new_member_session();
			switch_channel_set_name(switch_core_session_get_channel(coach_bridge_session), "coach-bridge");
			coach_bridge_uuid = switch_core_session_get_uuid(coach_bridge_session);
			app_args = cJSON_CreateObject();
			cJSON_AddStringToObject(app_args, "name", conference_name);
			cJSON_AddStringToObject(app_args, "coach_bridge", "{origination_external_id=coach-bridge-running}null/coach-bridge-running");
			args = cJSON_PrintUnformatted(app_args);
			switch_core_session_execute_application_async(coach_bridge_session, "conference", args);
			switch_safe_free(args);
			cJSON_Delete(app_args);
			switch_sleep(1000 * 3000);

			coach_bridge_target_session = switch_core_session_locate("coach-bridge-running");
			fst_requires(coach_bridge_target_session != NULL);
			switch_channel_set_name(switch_core_session_get_channel(coach_bridge_target_session), "coach-bridge-target");
			coach_bridge_target_uuid = switch_core_session_get_uuid(coach_bridge_target_session);

			// check member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member not to be a target of coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_bridge")), "Expect member not to be coaching over bridge");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_bridge_target")), "Expect member not to be target of coaching over bridge");
			member = get_member(conference, coach_bridge_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect coach-bridge member to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect coach-bridge member not to be a target of coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_bridge")), "Expect coach-bridge member to be coaching over bridge");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_bridge_target")), "Expect coach-bridge member not to be target of coaching over bridge");
			member = get_member(conference, coach_bridge_target_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect coach-bridge-target member not to be coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect coach-bridge-target member to be a target of coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_bridge")), "Expect coach-bridge-target member not to be coaching over bridge");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_bridge_target")), "Expect coach-bridge member to be target of coaching over bridge");
			cJSON_Delete(conference);

			fst_xcheck(verify_audio_path(member_session, coach_bridge_session, SWITCH_TRUE, coach_bridge_target_session, SWITCH_FALSE) == SWITCH_STATUS_SUCCESS, "Expect only coach-bridge can hear member");
			fst_xcheck(verify_audio_path(coach_bridge_session, member_session, SWITCH_FALSE, coach_bridge_target_session, SWITCH_TRUE) == SWITCH_STATUS_SUCCESS, "Expect only coach-bridge-target can hear coach-bridge");
			fst_xcheck(verify_audio_path(coach_bridge_target_session, member_session, SWITCH_TRUE, coach_bridge_session, SWITCH_TRUE) == SWITCH_STATUS_SUCCESS, "Expect coach-bridge and member can hear coach-bridge-target");

			// hang up bridge target member- this should kick the coach from the conference
			switch_channel_hangup(switch_core_session_get_channel(coach_bridge_target_session), SWITCH_CAUSE_NORMAL_CLEARING);

			switch_sleep(1000 * 1000);
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member not to be a target of coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_bridge")), "Expect member not to be coaching over bridge");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_bridge_target")), "Expect member not to be target of coaching over bridge");
			member = get_member(conference, coach_bridge_uuid);
			fst_xcheck(member == NULL, "Expect coach-bridge to be gone");
			member = get_member(conference, coach_bridge_target_uuid);
			fst_xcheck(member == NULL, "Expect coach-bridge-target to be gone");
			cJSON_Delete(conference);

			switch_core_session_rwunlock(coach_bridge_session);
			switch_core_session_rwunlock(coach_bridge_target_session);
		}
		FST_SESSION_END()

		/* Test coach-bridge API */
		FST_SESSION_BEGIN(coach_bridge_api_test)
		{
			const char *member_uuid = switch_core_session_get_uuid(fst_session);
			switch_core_session_t *fst_session_2 = NULL;
			const char *member_uuid_2 = NULL;
			const char *conference_name = member_uuid;
			cJSON *conference;
			cJSON *member;
			char *api_reply = NULL;

			fst_session_park(fst_session);

			// create a new conference
			switch_core_session_execute_application_async(fst_session, "conference", member_uuid);
			switch_sleep(1000 * 3000);

			// check initial member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			// set up coach bridge via API
			api_reply = exec_conference_api(conference_name, "coach-bridge", switch_core_sprintf(fst_pool, "uuid=%s {origination_external_id=coach-bridge-api}null/coach-bridge-api", member_uuid, member_uuid));
			fst_xcheck(api_reply != NULL && !strncmp("+OK ", api_reply, strlen("+OK ")), "Expect coach-bridge API to reply +OK");
			switch_safe_free(api_reply);
			switch_sleep(1000 * 1000);

			fst_session_2 = switch_core_session_locate("coach-bridge-api");
			fst_requires(fst_session_2 != NULL);
			member_uuid_2 = switch_core_session_get_uuid(fst_session_2);

			// check member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect coach bridge not to be coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect coach bridge to be a target of coaching");
			cJSON_Delete(conference);

			// hang up coaching member- this should kick the bridge from the conference
			switch_channel_hangup(switch_core_session_get_channel(fst_session), SWITCH_CAUSE_NORMAL_CLEARING);

			switch_sleep(1000 * 1000);
			conference = json_list_local_conference(conference_name);
			fst_xcheck(conference == NULL, "Expect conference to be gone");
			cJSON_Delete(conference);

			switch_channel_hangup(switch_core_session_get_channel(fst_session_2), SWITCH_CAUSE_NORMAL_CLEARING);
			switch_core_session_rwunlock(fst_session_2);
		}
		FST_SESSION_END()

		/* Test coach-bridge API with dial handle as dialstring */
		FST_SESSION_BEGIN(coach_bridge_json_api_test)
		{
			const char *member_uuid = switch_core_session_get_uuid(fst_session);
			switch_core_session_t *fst_session_2 = NULL;
			const char *member_uuid_2 = NULL;
			const char *conference_name = member_uuid;
			cJSON *conference;
			cJSON *member;
			char *api_reply = NULL;
			switch_dial_handle_t *dh = NULL;
			switch_dial_leg_list_t *ll = NULL;
			switch_dial_leg_t *leg = NULL;
			char *coach_bridge_json_str = NULL;

			fst_session_park(fst_session);

			// create a new conference
			switch_core_session_execute_application_async(fst_session, "conference", member_uuid);
			switch_sleep(1000 * 3000);

			// check initial member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			// set up coach bridge via API
			switch_dial_handle_create(&dh);
			switch_dial_handle_add_leg_list(dh, &ll);
			switch_dial_leg_list_add_leg(ll, &leg, "null/coach-bridge-json-api");
			switch_dial_handle_add_leg_var(leg, "origination_external_id", "coach-bridge-json-api");
			switch_dial_handle_serialize_json(dh, &coach_bridge_json_str);
			switch_dial_handle_destroy(&dh);
			api_reply = exec_conference_api(conference_name, "coach-bridge", switch_core_sprintf(fst_pool, "uuid=%s %s", member_uuid, coach_bridge_json_str));
			switch_safe_free(coach_bridge_json_str);
			fst_xcheck(api_reply != NULL && !strncmp("+OK ", api_reply, strlen("+OK ")), "Expect coach-bridge API to reply +OK");
			switch_safe_free(api_reply);
			switch_sleep(1000 * 1000);

			fst_session_2 = switch_core_session_locate("coach-bridge-json-api");
			fst_requires(fst_session_2 != NULL);
			member_uuid_2 = switch_core_session_get_uuid(fst_session_2);

			// check member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect coach bridge not to be coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect coach bridge to be a target of coaching");
			cJSON_Delete(conference);

			// hang up coaching member- this should kick the bridge from the conference
			switch_channel_hangup(switch_core_session_get_channel(fst_session), SWITCH_CAUSE_NORMAL_CLEARING);

			switch_sleep(1000 * 1000);
			conference = json_list_local_conference(conference_name);
			fst_xcheck(conference == NULL, "Expect conference to be gone");
			cJSON_Delete(conference);

			switch_channel_hangup(switch_core_session_get_channel(fst_session_2), SWITCH_CAUSE_NORMAL_CLEARING);
			switch_core_session_rwunlock(fst_session_2);
		}
		FST_SESSION_END()

		/* Test coach bridge hangup after bridge created with coach-bridge API */
		FST_SESSION_BEGIN(coach_bridge_api_hangup_test)
		{
			const char *member_uuid = switch_core_session_get_uuid(fst_session);
			switch_core_session_t *fst_session_2 = NULL;
			const char *member_uuid_2 = NULL;
			const char *conference_name = member_uuid;
			cJSON *conference;
			cJSON *member;
			char *api_reply = NULL;

			fst_session_park(fst_session);

			// create a new conference
			switch_core_session_execute_application_async(fst_session, "conference", member_uuid);
			switch_sleep(1000 * 3000);

			// check initial member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			// set up coach bridge via API
			api_reply = exec_conference_api(conference_name, "coach-bridge", switch_core_sprintf(fst_pool, "uuid=%s {origination_external_id=coach-bridge-api}null/coach-bridge-api", member_uuid, member_uuid));
			fst_xcheck(api_reply != NULL && !strncmp("+OK ", api_reply, strlen("+OK ")), "Expect coach-bridge API to reply +OK");
			switch_safe_free(api_reply);
			switch_sleep(1000 * 1000);

			fst_session_2 = switch_core_session_locate("coach-bridge-api");
			fst_requires(fst_session_2 != NULL);
			member_uuid_2 = switch_core_session_get_uuid(fst_session_2);

			// check member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect coach bridge not to be coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect coach bridge to be a target of coaching");
			cJSON_Delete(conference);

			// hang up bridge member- this should kick the coach from the conference
			switch_channel_hangup(switch_core_session_get_channel(fst_session_2), SWITCH_CAUSE_NORMAL_CLEARING);

			switch_sleep(1000 * 1000);
			conference = json_list_local_conference(conference_name);
			fst_xcheck(conference == NULL, "Expect conference to be gone");
			cJSON_Delete(conference);

			switch_channel_hangup(switch_core_session_get_channel(fst_session_2), SWITCH_CAUSE_NORMAL_CLEARING);
			switch_core_session_rwunlock(fst_session_2);
		}
		FST_SESSION_END()

		/* Test failure to dial in coach-bridge API */
		FST_SESSION_BEGIN(coach_bridge_api_error_test)
		{
			const char *member_uuid = switch_core_session_get_uuid(fst_session);
			switch_core_session_t *fst_session_2 = NULL;
			const char *conference_name = member_uuid;
			cJSON *conference;
			cJSON *member;
			char *api_reply = NULL;

			fst_session_park(fst_session);

			// create a new conference
			switch_core_session_execute_application_async(fst_session, "conference", member_uuid);
			switch_sleep(1000 * 3000);

			// check initial member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			// set up coach bridge via API
			api_reply = exec_conference_api(conference_name, "coach-bridge", switch_core_sprintf(fst_pool, "uuid=%s {origination_external_id=coach-bridge-error}error/user_busy", member_uuid));
			fst_xcheck(api_reply != NULL && !strncmp("-ERR ", api_reply, strlen("-ERR ")), "Expect coach-bridge API to reply -ERR");
			switch_safe_free(api_reply);
			switch_sleep(1000 * 1000);

			fst_session_2 = switch_core_session_locate("coach-bridge-api");
			fst_xcheck(fst_session_2 == NULL, "Expect bridge call to be gone");

			// check member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);
		}
		FST_SESSION_END()

		/* Use coach-stop API to stop an existing coach bridge */
		FST_SESSION_BEGIN(coach_bridge_api_stop_test)
		{
			const char *member_uuid = switch_core_session_get_uuid(fst_session);
			switch_core_session_t *fst_session_2 = NULL;
			const char *member_uuid_2 = NULL;
			const char *conference_name = member_uuid;
			cJSON *conference;
			cJSON *member;
			char *api_reply = NULL;

			fst_session_park(fst_session);

			// create a new conference
			switch_core_session_execute_application_async(fst_session, "conference", member_uuid);
			switch_sleep(1000 * 3000);

			// check initial member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			// set up coach bridge via API
			api_reply = exec_conference_api(conference_name, "coach-bridge", switch_core_sprintf(fst_pool, "uuid=%s {origination_external_id=coach-bridge-api}null/coach-bridge-api", member_uuid, member_uuid));
			fst_xcheck(api_reply != NULL && !strncmp("+OK ", api_reply, strlen("+OK ")), "Expect coach-bridge API to reply +OK");
			switch_safe_free(api_reply);
			switch_sleep(1000 * 1000);

			fst_session_2 = switch_core_session_locate("coach-bridge-api");
			fst_requires(fst_session_2 != NULL);
			member_uuid_2 = switch_core_session_get_uuid(fst_session_2);

			// check member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect coach bridge not to be coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect coach bridge to be a target of coaching");
			cJSON_Delete(conference);

			// stop coaching- this should kick the bridge from the conference
			api_reply = exec_conference_api(conference_name, "coach-stop", switch_core_sprintf(fst_pool, "uuid=%s", member_uuid));
			fst_xcheck(api_reply != NULL && !strncmp("+OK ", api_reply, strlen("+OK ")), "Expect coach-stop API to reply +OK");
			switch_safe_free(api_reply);
			switch_sleep(1000 * 1000);

			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			member = get_member(conference, member_uuid_2);
			fst_xcheck(member == NULL, "Expect coach bridge to be gone");
			cJSON_Delete(conference);

			switch_channel_hangup(switch_core_session_get_channel(fst_session_2), SWITCH_CAUSE_NORMAL_CLEARING);
			switch_core_session_rwunlock(fst_session_2);
		}
		FST_SESSION_END()

		/* Use coach-bridge API to replace an existing coach bridge */
		FST_SESSION_BEGIN(coach_bridge_api_replace_test)
		{
			const char *member_uuid = switch_core_session_get_uuid(fst_session);
			switch_core_session_t *fst_session_2 = NULL;
			const char *member_uuid_2 = NULL;
			switch_core_session_t *fst_session_3 = NULL;
			const char *member_uuid_3 = NULL;
			const char *conference_name = member_uuid;
			cJSON *conference;
			cJSON *member;
			char *api_reply = NULL;

			fst_session_park(fst_session);

			// create a new conference
			switch_core_session_execute_application_async(fst_session, "conference", member_uuid);
			switch_sleep(1000 * 3000);

			// check initial member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 not to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			cJSON_Delete(conference);

			// set up coach bridge via API
			api_reply = exec_conference_api(conference_name, "coach-bridge", switch_core_sprintf(fst_pool, "uuid=%s {origination_external_id=coach-bridge-api}null/coach-bridge-api", member_uuid, member_uuid));
			fst_xcheck(api_reply != NULL && !strncmp("+OK ", api_reply, strlen("+OK ")), "Expect coach API to reply +OK");
			switch_safe_free(api_reply);
			switch_sleep(1000 * 1000);

			fst_session_2 = switch_core_session_locate("coach-bridge-api");
			fst_requires(fst_session_2 != NULL);
			member_uuid_2 = switch_core_session_get_uuid(fst_session_2);

			// check member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect coach bridge not to be coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect coach bridge to be a target of coaching");
			cJSON_Delete(conference);

			// start coaching a new bridge- this should kick the current bridge from the conference
			api_reply = exec_conference_api(conference_name, "coach-bridge", switch_core_sprintf(fst_pool, "uuid=%s {origination_external_id=coach-bridge-api-2}null/coach-bridge-api", member_uuid, member_uuid));
			fst_xcheck(api_reply != NULL && !strncmp("+OK ", api_reply, strlen("+OK ")), "Expect coach-bridge API to reply +OK");
			switch_safe_free(api_reply);
			switch_sleep(1000 * 1000);

			fst_session_3 = switch_core_session_locate("coach-bridge-api-2");
			fst_requires(fst_session_3 != NULL);
			member_uuid_3 = switch_core_session_get_uuid(fst_session_3);

			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 1 to be coaching");
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 1 not to be a target of coaching");
			member = get_member(conference, member_uuid_2);
			fst_xcheck(member == NULL, "Expect coach bridge to be gone");
			member = get_member(conference, member_uuid_3);
			fst_requires(member != NULL);
			fst_xcheck(cJSON_IsFalse(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach")), "Expect member 3 not to be coaching");
			fst_xcheck(cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(member, "flags"), "is_coach_target")), "Expect member 3 to be a target of coaching");
			cJSON_Delete(conference);

			switch_channel_hangup(switch_core_session_get_channel(fst_session_2), SWITCH_CAUSE_NORMAL_CLEARING);
			switch_core_session_rwunlock(fst_session_2);

			// hang up target - this will hang up the coach and end the conference
			switch_channel_hangup(switch_core_session_get_channel(fst_session_3), SWITCH_CAUSE_NORMAL_CLEARING);
			switch_core_session_rwunlock(fst_session_3);
			switch_sleep(1000 * 1000);

			conference = json_list_local_conference(conference_name);
			fst_xcheck(conference == NULL, "Expect conference to be gone");
			cJSON_Delete(conference);
		}
		FST_SESSION_END()

		/* set up 3 party conference and validate audio paths between each party */
		FST_SESSION_BEGIN(happy_audio_test)
		{
			const char *member_uuid = switch_core_session_get_uuid(fst_session);
			switch_core_session_t *fst_session_2 = NULL;
			const char *member_uuid_2 = NULL;
			switch_core_session_t *fst_session_3 = NULL;
			const char *member_uuid_3 = NULL;
			const char *conference_name = member_uuid;
			cJSON *conference;
			cJSON *member;

			fst_session_park(fst_session);

			// create a new conference with three members
			switch_channel_set_name(switch_core_session_get_channel(fst_session), "member-1");
			switch_core_session_execute_application_async(fst_session, "conference", conference_name);
			switch_sleep(1000 * 1000);
			fst_session_2 = new_member_session();
			switch_channel_set_name(switch_core_session_get_channel(fst_session_2), "member-2");
			member_uuid_2 = switch_core_session_get_uuid(fst_session_2);
			switch_core_session_execute_application_async(fst_session_2, "conference", conference_name);
			switch_sleep(1000 * 1000);
			fst_session_3 = new_member_session();
			switch_channel_set_name(switch_core_session_get_channel(fst_session_3), "member-3");
			member_uuid_3 = switch_core_session_get_uuid(fst_session_3);
			switch_core_session_execute_application_async(fst_session_3, "conference", conference_name);
			switch_sleep(1000 * 3000);

			// check member flags
			conference = json_list_local_conference(conference_name);
			fst_requires(conference != NULL);
			member = get_member(conference, member_uuid);
			fst_requires(member != NULL);
			member = get_member(conference, member_uuid_2);
			fst_requires(member != NULL);
			member = get_member(conference, member_uuid_3);
			fst_requires(member != NULL);
			cJSON_Delete(conference);

			switch_channel_hangup(switch_core_session_get_channel(fst_session_2), SWITCH_CAUSE_NORMAL_CLEARING);
			switch_core_session_rwunlock(fst_session_2);

			switch_channel_hangup(switch_core_session_get_channel(fst_session_3), SWITCH_CAUSE_NORMAL_CLEARING);
			switch_core_session_rwunlock(fst_session_3);
		}
		FST_SESSION_END()
	}
	FST_SUITE_END()
}
FST_CORE_END()
