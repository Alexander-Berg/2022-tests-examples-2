INSERT INTO agent.gp_dsp_operator_activity_daily(
	login, date, last_update, quality_coeff_consultation_sum_pcnt, quality_coeff_order_placing_sum_pcnt, quality_coeff_consultation_cnt, quality_coeff_order_placing_cnt, delay_cnt, abcense_cnt, claim_cnt, call_cnt, success_order_cnt)
	VALUES ('andrey', NOW()::date, NOW(), 0, 0, 0, 0, 0, 0, 0, 0, 0);
