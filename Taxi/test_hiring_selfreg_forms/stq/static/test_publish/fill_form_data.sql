UPDATE hiring_selfreg_forms.forms_completion
SET form_data = '{form_data}'
WHERE form_completion_id = '{form_completion_id}'
RETURNING form_completion_id;
