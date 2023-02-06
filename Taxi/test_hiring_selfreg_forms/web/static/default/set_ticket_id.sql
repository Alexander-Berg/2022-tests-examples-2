UPDATE hiring_selfreg_forms.forms_completion
SET ticket_id = '{ticket_id}'
WHERE form_completion_id = '{form_completion_id}'
RETURNING ticket_id
