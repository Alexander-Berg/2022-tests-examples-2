ALTER TABLE balancers.entry_points
    DROP CONSTRAINT entry_points_check1,
    ADD CONSTRAINT shared_not_external_check CHECK ( NOT (is_external AND can_share_namespace) ),

    DROP CONSTRAINT entry_points_check2,
    ADD CONSTRAINT external_non_https CHECK ( NOT (is_external AND protocol != 'https') )
;
