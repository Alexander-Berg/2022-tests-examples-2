INSERT INTO agent.gp_details_quality (
    ticket_code,
    operator_login,
    utc_updated_dttm,
    utc_resolved_dttm,
    utc_dialog_dttm,
    commutation_queue_code,
    ticket_type_code,
    score_total,
    dialog_url,
    auditor_comment)
VALUES
('AUDKON-1','webalex',NOW(),NOW(),NOW(),'test','test',0,'test_url','test'),
('AUDKON-3906747','webalex',NOW(),NOW(),NOW(),'test','test',0,'test_url','test');
