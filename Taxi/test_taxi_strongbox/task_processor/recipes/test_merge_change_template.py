async def test_recipe(load_yaml, task_processor, run_job_common, mockserver):

    recipe = task_processor.load_recipe(
        load_yaml('recipes/ArcadiaChangeTemplate.yaml')['data'],
    )
    await task_processor.start_job(
        name='ArcadiaMergeDiffProposalWithPR',
        job_vars={
            'pull_request_url': 'mocked_pull_request_url',
            'st_ticket': 'COOLTICKET-1',
            'automerge': True,
            'diff_proposal': {},
        },
        initiator='taxi-strongbox',
        idempotency_token='idempotency_token_1',
    )
    job = await recipe.start_job(
        job_vars={
            'st_ticket': 'COOLTICKET-1',
            'diff_proposal': {},
            'automerge': False,
            'initiator': 'taxi-strongbox',
            'reviewers': ['deoevgen'],
            'approve_required': False,
            'service_name': 'some_service',
            'type_name': 'secdist',
            'with_pr': True,
        },
        initiator='taxi-strongbox',
        idempotency_token='some_service_secdist_1',
    )
    await run_job_common(job)
