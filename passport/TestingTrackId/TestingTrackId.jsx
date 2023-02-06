import React from 'react';
import PropTypes from 'prop-types';
import {useSelector} from 'react-redux';

export default function TestingTrackId({trackId}) {
    const env = useSelector(({settings = {}}) => settings.env || {});
    const defaultTrackId = useSelector(({common = {}}) => common.track_id);
    const isNotProduction = env.type === 'development' || env.type === 'testing';

    if (isNotProduction) {
        return <span aria-label={trackId || defaultTrackId} id='test_track_id' />;
    }

    return null;
}

TestingTrackId.propTypes = {
    trackId: PropTypes.string
};
