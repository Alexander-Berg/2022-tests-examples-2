exports.deps = [
    // i-bem and stuff
    {block: 'i-bem'},
    {block: 'i-bem', elem: 'dom'},
    {block: 'i-bem', elem: 'json', mod: 'escape', val: 'yes'},

    {block: 'i-content', mod: 'type', val: 'bemhtml'},
    {block: 'lodash'},

    {block: 'i-filter-simple'},
    {block: 'i-filter-multidim'},
    {block: 'i-filter-tree'},
    {block: 'i-filter-cohort'},
    {block: 'i-filter-cohort-segment'},
    {block: 'i-filters'},

    // models
    {block: 'promised-models', elem: 'model'},
    {block: 'promised-models', elem: 'registry'},
    {block: 'promised-models', elem: 'registry-storage'},

    {block: 'i-statefull-block'},

    {block: 'segment'},
    {block: 'segments-list'},
    {block: 'segmentation'},
    {block: 'segment-settings'},
    {block: 'multiselect'},
    {block: 'filter-multiselect'},
    {block: 'segment-cohorts-list'},
    {block: 'm-segmentation'},
    {block: 'm-filter-multiselect'},
    {block: 'm-segment-cohorts-list'},
    {block: 'segment-tags-list'},
    {block: 'segment-tag'}
];
