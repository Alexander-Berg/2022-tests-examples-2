import {getClosestReport, Report} from '../collectMetrics';

test('getClosestReport', () => {
    const average = 50;
    const reports: Report[] = [
        {categories: {performance: {score: 30}}} as Report,
        {categories: {performance: {score: 40}}} as Report,
        {categories: {performance: {score: 55}}} as Report,
        {categories: {performance: {score: 49}}} as Report,
        {categories: {performance: {score: 60}}} as Report
    ];

    const closest = getClosestReport(reports, average);

    expect(closest).toBe(reports[3]);
    expect(closest.categories.performance.score).toBe(average);
});
