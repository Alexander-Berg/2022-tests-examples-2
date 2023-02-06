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
 * Chris Seven Du <seven@signalwire>
 *
 *
 * switch_ivr_play_say.c -- IVR tests
 *
 */
#include <test/switch_test.h>

#define MIN_FRAME_LEN 2
#define MAX_FRAME_LEN 5

#define RENACK_TIME 100000

FST_CORE_BEGIN("./conf")
{
	FST_SUITE_BEGIN()
	{
		FST_SETUP_BEGIN()
		{

		}
		FST_SETUP_END()

		FST_TEST_BEGIN(jb_test)
		{
			switch_jb_t *vb = NULL;
			switch_jb_create(&vb, SJB_VIDEO, 2, 5, fst_pool, SJB_NONE, NULL);
			// switch_jb_set_session(vb, session);
			switch_jb_debug_level(vb, 10);
			switch_jb_destroy(&vb);
		}
		FST_TEST_END()

		FST_TEST_BEGIN(jb_test_put_get_ok)
		{
			int i;
			uint32_t ts = 0;
			switch_status_t status;
			switch_rtp_packet_t *send_msg;
			switch_rtp_hdr_t *header;
			switch_jb_t *vb = NULL;
			switch_size_t bytes = 1024;
			switch_jb_create(&vb, SJB_VIDEO, MIN_FRAME_LEN, MAX_FRAME_LEN, fst_pool, SJB_NONE, NULL);
			// switch_jb_set_session(vb, session);
			switch_jb_debug_level(vb, 10);

			send_msg = malloc(sizeof(switch_rtp_packet_t));

			fst_requires(send_msg);

			header = (switch_rtp_hdr_t *)send_msg;

			header->version = 2;
			header->seq = 0;
			header->ts = 0;
			header->pt = 96;
			header->m = 0;

			for (i = 0; i < 10; i++) {
				header->seq = htons(i);
				header->m = i % 2;
				if (header->m == 0) {
					ts += 3000;
					header->ts = ntohl(ts);
				}
				status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
				fst_check(status == SWITCH_STATUS_SUCCESS);
			}

			status = switch_jb_get_packet(vb, send_msg, &bytes);
			switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "status: %d bytes: %"SWITCH_SIZE_T_FMT"\n", status, bytes);
			fst_check(status == SWITCH_STATUS_SUCCESS);
            header = (switch_rtp_hdr_t *)send_msg;
            fst_check(ntohs(header->seq) == 0);

			status = switch_jb_get_packet_by_seq(vb, htons(2), send_msg, &bytes);
			switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "status: %d bytes: %"SWITCH_SIZE_T_FMT" seq: %d\n", status, bytes, ntohs(header->seq));
			fst_check(status == SWITCH_STATUS_SUCCESS);
            header = (switch_rtp_hdr_t *)send_msg;
            fst_check(ntohs(header->seq) == 2);

			free(send_msg);
			switch_jb_destroy(&vb);
		}
		FST_TEST_END()

		FST_TEST_BEGIN(jb_test_put_get_overflow)
		{
			int i = 0;
			uint32_t ts = 0;
			switch_status_t status;
			switch_rtp_packet_t *send_msg;
			switch_rtp_hdr_t *header;
			switch_jb_t *vb = NULL;
			switch_size_t bytes = 1024;
			switch_jb_create(&vb, SJB_VIDEO, MIN_FRAME_LEN, MAX_FRAME_LEN, fst_pool, SJB_NONE, NULL);
			// switch_jb_set_session(vb, session);
			switch_jb_debug_level(vb, 10);

			send_msg = malloc(sizeof(switch_rtp_packet_t));

			fst_requires(send_msg);

			header = (switch_rtp_hdr_t *)send_msg;

			header->version = 2;
			header->seq = 0;
			header->ts = 0;
			header->pt = 96;
			header->m = 0;

			for (i = 0; i < 10; i++) {
				header->seq = htons(i);
				header->m = i % 2;
				if (header->m == 0) {
					ts += 3000;
					header->ts = ntohl(ts);
				}
				status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
				fst_check(status == SWITCH_STATUS_SUCCESS);
			}

			status = switch_jb_get_packet(vb, send_msg, &bytes);
			switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "status: %d bytes: %"SWITCH_SIZE_T_FMT"\n", status, bytes);
			fst_check(status == SWITCH_STATUS_SUCCESS);
			header = (switch_rtp_hdr_t *)send_msg;
			fst_check(ntohs(header->seq) == 0);

			status = switch_jb_get_packet_by_seq(vb, htons(2), send_msg, &bytes);
			switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "status: %d bytes: %"SWITCH_SIZE_T_FMT" seq: %d\n", status, bytes, ntohs(header->seq));
			fst_check(status == SWITCH_STATUS_SUCCESS);
			header = (switch_rtp_hdr_t *)send_msg;
			fst_check(ntohs(header->seq) == 2);

			free(send_msg);
			switch_jb_destroy(&vb);
		}
		FST_TEST_END()

		FST_TEST_BEGIN(jb_test_put_get_punt)
		{
			int i = 0;
			uint32_t ts = 0;
			switch_status_t status;
			switch_rtp_packet_t *send_msg;
			switch_rtp_hdr_t *header;
			switch_jb_t *vb = NULL;
			switch_size_t bytes = 1024;
			switch_jb_create(&vb, SJB_VIDEO, MIN_FRAME_LEN, MAX_FRAME_LEN, fst_pool, SJB_NONE, NULL);
			// switch_jb_set_session(vb, session);
			switch_jb_debug_level(vb, 10);

			send_msg = malloc(sizeof(switch_rtp_packet_t));

			fst_requires(send_msg);

			header = (switch_rtp_hdr_t *)send_msg;

			header->version = 2;
			header->seq = 0;
			header->ts = 0;
			header->pt = 96;
			header->m = 0;

			for (i = 0; i < 10; i++) {
                if (i == 2) ts += 900000 * 5 + 1; // seq 2 has more diff, will trigger a reset
				header->seq = htons(i);
				header->m = i % 2;
				if (header->m == 0) {
					ts += 3000;
					header->ts = ntohl(ts);
				}
				status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
				fst_check(status == SWITCH_STATUS_SUCCESS);
			}

			status = switch_jb_get_packet(vb, send_msg, &bytes);
			switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "status: %d bytes: %"SWITCH_SIZE_T_FMT"\n", status, bytes);
			fst_check(status == SWITCH_STATUS_SUCCESS);
            header = (switch_rtp_hdr_t *)send_msg;
            fst_check(ntohs(header->seq) == 2);

			status = switch_jb_get_packet_by_seq(vb, htons(2), send_msg, &bytes);
			switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "status: %d bytes: %"SWITCH_SIZE_T_FMT"\n", status, bytes);
			fst_check(status == SWITCH_STATUS_NOTFOUND);

			free(send_msg);
			switch_jb_destroy(&vb);
		}
		FST_TEST_END()

		FST_TEST_BEGIN(jb_test_put_get_not_found)
		{
			switch_jb_t *vb = NULL;
			int i = 0;
			uint32_t ts = 0;
			switch_status_t status;
			switch_rtp_packet_t *send_msg;
			switch_rtp_hdr_t *header;
			switch_size_t bytes = 1024;
			switch_jb_create(&vb, SJB_VIDEO, MIN_FRAME_LEN, MAX_FRAME_LEN, fst_pool, SJB_NONE, NULL);
			// switch_jb_set_session(vb, session);
			switch_jb_debug_level(vb, 10);

			send_msg = malloc(sizeof(switch_rtp_packet_t));

			fst_requires(send_msg);

			header = (switch_rtp_hdr_t *)send_msg;

			header->version = 2;
			header->seq = 0;
			header->ts = 0;
			header->pt = 96;
			header->m = 0;

			for (i = 0; i < MAX_FRAME_LEN * 5; i++) {
				header->seq = htons(i);
				header->m = i % 2;
				if (header->m == 0) {
					ts += 3000;
					header->ts = ntohl(ts);
				}
				status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
				fst_check(status == SWITCH_STATUS_SUCCESS);
			}

			status = switch_jb_get_packet(vb, send_msg, &bytes);
			switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "status: %d bytes: %"SWITCH_SIZE_T_FMT" seq: %d\n", status, bytes, ntohs(header->seq));
			fst_check(status == SWITCH_STATUS_SUCCESS);

			status = switch_jb_get_packet_by_seq(vb, htons(2), send_msg, &bytes);
			switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "status: %d bytes: %"SWITCH_SIZE_T_FMT"\n", status, bytes);
			fst_check(status == SWITCH_STATUS_NOTFOUND);

			free(send_msg);
			switch_jb_destroy(&vb);
		}
		FST_TEST_END()


		FST_TEST_BEGIN(jb_test_put_get_jitter)
		{
			switch_jb_t *vb = NULL;
			int i = 0;
			uint32_t ts = 0;
			switch_status_t status;
			switch_rtp_packet_t *send_msg;
			switch_rtp_hdr_t *header;
			switch_size_t bytes = 1024;
			switch_jb_create(&vb, SJB_VIDEO, MIN_FRAME_LEN, MAX_FRAME_LEN, fst_pool, SJB_NONE, NULL);
			// switch_jb_set_session(vb, session);
			switch_jb_debug_level(vb, 10);

			send_msg = malloc(sizeof(switch_rtp_packet_t));

			fst_requires(send_msg);

			header = (switch_rtp_hdr_t *)send_msg;

			header->version = 2;
			header->seq = 0;
			header->ts = 0;
			header->pt = 96;
			header->m = 0;

			for (i = 0; i < 3; i++) {
				header->seq = htons(i);
				header->m = i % 2;
				if (header->m == 0) {
					ts += 3000;
					header->ts = ntohl(ts);
				}
				status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
				fst_check(status == SWITCH_STATUS_SUCCESS);
			}

			header->seq = htons(4);
			status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
			fst_check(status == SWITCH_STATUS_SUCCESS);
			header->seq = htons(3);
			status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
			fst_check(status == SWITCH_STATUS_SUCCESS);

			for (i = 5; i < 10; i++) {
				header->seq = htons(i);
				header->m = i % 2;
				if (header->m == 0) {
					ts += 3000;
					header->ts = ntohl(ts);
				}
				status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
				fst_check(status == SWITCH_STATUS_SUCCESS);
			}


			for (i = 0; i < 7; i++) {
				status = switch_jb_get_packet(vb, send_msg, &bytes);
				switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "status: %d bytes: %"SWITCH_SIZE_T_FMT" seq: %d\n", status, bytes, ntohs(header->seq));
				fst_check(status == SWITCH_STATUS_SUCCESS);
				fst_check(i == ntohs(header->seq));
			}

			status = switch_jb_get_packet(vb, send_msg, &bytes);
			switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "status: %d bytes: %"SWITCH_SIZE_T_FMT" seq: %d\n", status, bytes, ntohs(header->seq));
			fst_check(status == SWITCH_STATUS_MORE_DATA);

			free(send_msg);
			switch_jb_destroy(&vb);
		}
		FST_TEST_END()

		FST_TEST_BEGIN(jb_test_put_get_dup)
		{
			switch_jb_t *vb = NULL;
			int i = 0;
			uint32_t ts = 0;
			switch_status_t status;
			switch_rtp_packet_t *send_msg;
			switch_rtp_hdr_t *header;
			switch_size_t bytes = 1024;
			switch_jb_create(&vb, SJB_VIDEO, MIN_FRAME_LEN, MAX_FRAME_LEN, fst_pool, SJB_NONE, NULL);
			// switch_jb_set_session(vb, session);
			switch_jb_debug_level(vb, 10);

			send_msg = malloc(sizeof(switch_rtp_packet_t));

			fst_requires(send_msg);

			header = (switch_rtp_hdr_t *)send_msg;

			header->version = 2;
			header->seq = 0;
			header->ts = 0;
			header->pt = 96;
			header->m = 0;

			for (i = 0; i < 3; i++) {
				header->seq = htons(i);
				header->m = i % 2;
				if (header->m == 0) {
					ts += 3000;
					header->ts = ntohl(ts);
				}
				status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
				fst_check(status == SWITCH_STATUS_SUCCESS);
			}

			ts = 3000;

			// duplicated packets
			for (i = 1; i < 10; i++) {
				header->seq = htons(i);
				header->m = i % 2;
				if (header->m == 0) {
					ts += 3000;
					header->ts = ntohl(ts);
				}
				status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
				fst_check(status == SWITCH_STATUS_SUCCESS);
			}

			for (i = 0; i < 7; i++) {
				status = switch_jb_get_packet(vb, send_msg, &bytes);
				switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "status: %d bytes: %"SWITCH_SIZE_T_FMT" seq: %d\n", status, bytes, ntohs(header->seq));
				fst_check(status == SWITCH_STATUS_SUCCESS);
				fst_check(i == ntohs(header->seq));
			}

			free(send_msg);
			switch_jb_destroy(&vb);
		}
		FST_TEST_END()

		FST_TEST_BEGIN(jb_test_nack)
		{
			switch_jb_t *vb = NULL;
			uint32_t seq;
			uint32_t nack;
			int i = 0;
			uint32_t ts = 0;
			switch_status_t status;
			switch_rtp_packet_t *send_msg;
			switch_rtp_hdr_t *header;
			switch_size_t bytes = 1024;
			switch_jb_create(&vb, SJB_VIDEO, MIN_FRAME_LEN, MAX_FRAME_LEN, fst_pool, SJB_NONE, NULL);
			switch_jb_debug_level(vb, 10);

			send_msg = malloc(sizeof(switch_rtp_packet_t));

			fst_requires(send_msg);

			header = (switch_rtp_hdr_t *)send_msg;

			header->version = 2;
			header->seq = 0;
			header->ts = 0;
			header->pt = 96;
			header->m = 0;

			for (i = 0; i < 3; i++) {
				header->seq = htons(i);
				header->m = i % 2;
				if (header->m == 0) {
					ts += 3000;
					header->ts = ntohl(ts);
				}
				status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
				fst_check(status == SWITCH_STATUS_SUCCESS);
			}

			nack = switch_jb_pop_nack(vb);
			fst_check(nack == 0);

			header->seq = htons(3);
			status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
			fst_check(status == SWITCH_STATUS_SUCCESS);
			header->seq = htons(5);
			status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
			fst_check(status == SWITCH_STATUS_SUCCESS);

			nack = switch_jb_pop_nack(vb);
			seq = ntohs(nack & 0xFFFF);
			switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "Nackable Seq: [%u]\n", seq);
			fst_check(seq == 4);

			// again

			switch_sleep(101 * 1000); // wait 101 milliseconds
			nack = switch_jb_pop_nack(vb); 
			seq = ntohs(nack & 0xFFFF);
			switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "Nackable Seq: [%u]\n", seq);
			fst_check(seq == 4);

			// wait to expire 

			switch_sleep(RENACK_TIME * 10  + 1);
			nack = switch_jb_pop_nack(vb);
			fst_check(nack == 0);

			free(send_msg);
			switch_jb_destroy(&vb);
		}
		FST_TEST_END()

		FST_TEST_BEGIN(jb_test_nack_ulpfec)
		{
			switch_jb_t *vb = NULL;
			uint32_t seq;
			uint32_t nack;
			uint32_t ts = 0;
			switch_status_t status;
			switch_rtp_packet_t *send_msg;
			switch_rtp_hdr_t *header;
			switch_size_t bytes = 1024;
			switch_jb_create(&vb, SJB_VIDEO, MIN_FRAME_LEN, MAX_FRAME_LEN, fst_pool, SJB_NONE, NULL);
			switch_jb_debug_level(vb, 10);

			send_msg = malloc(sizeof(switch_rtp_packet_t));

			fst_requires(send_msg);

 
			header = (switch_rtp_hdr_t *)send_msg;

			header->version = 2;
			header->seq = 0;
			header->ts = 0;
			header->pt = 96;
			header->m = 0;

			header->seq = htons(1);
			status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
			fst_check(status == SWITCH_STATUS_SUCCESS);

			ts += 3000;
			header->ts = ntohl(ts);

			header->seq = htons(2);
			status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
			fst_check(status == SWITCH_STATUS_SUCCESS);

			ts += 3000;
			header->ts = ntohl(ts);

			nack = switch_jb_pop_nack(vb);
			fst_check(nack == 0);

			header->seq = htons(3);
			status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
			fst_check(status == SWITCH_STATUS_SUCCESS);
			
			ts += 6000;  // skip 1 seq
			header->ts = ntohl(ts);

			header->seq = htons(5);
			status = switch_jb_put_packet(vb, (switch_rtp_packet_t *)send_msg, bytes, SWITCH_FALSE);
			fst_check(status == SWITCH_STATUS_SUCCESS);

			switch_jb_set_flag(vb, SJB_NONE | SJB_HAS_ULPFEC); // set flag to simulate JB with FEC

			switch_jb_set_nack_fec_combo(vb);

			switch_jb_set_rtt(vb, 0);

			nack = switch_jb_pop_nack(vb);
			seq = ntohs(nack & 0xFFFF);
			switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "Nackable Seq: [%u]\n", seq);
			fst_check(seq == 4);

			// again

			switch_sleep(101 * 1000); // wait 101 milliseconds
			nack = switch_jb_pop_nack(vb); 
			seq = ntohs(nack & 0xFFFF);
			switch_log_printf(SWITCH_CHANNEL_LOG, SWITCH_LOG_INFO, "Nackable Seq: [%u]\n", seq);
			fst_check(seq == 4);

			// wait to expire. when RTT over 1 sec NACK gets special treatment - we expire with RTT
			switch_jb_set_rtt(vb, 1);

			switch_sleep(1120 * 1000 + 1); // wait more than rtt
			nack = switch_jb_pop_nack(vb); 
			fst_check(nack == 0);

			free(send_msg);
			switch_jb_clear_flag(vb, SJB_HAS_ULPFEC); // clear flag to avoid calling destroy on hash tables that we didn't init.
			switch_jb_destroy(&vb);
		}
		FST_TEST_END()

		FST_TEARDOWN_BEGIN()
		{
		}
		FST_TEARDOWN_END()
	}
	FST_SUITE_END()
}
FST_CORE_END()
