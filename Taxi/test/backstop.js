const styleguideConfig = require('../styleguide.config');
const styleguideSections = styleguideConfig.sections;

const config = {
    id: 'amber-blocks',
    viewports: [
        {
            label: 'desktop',
            width: 1200,
            height: 1000
        }
    ],
    onBeforeScript: 'puppet/onBefore.js',
    onReadyScript: 'puppet/onReady.js',
    scenarios: [...createScenariosFromConfig(styleguideSections)],
    paths: {
        bitmaps_reference: 'test/backstop_data/bitmaps_reference',
        bitmaps_test: 'test/backstop_data/bitmaps_test',
        engine_scripts: 'test/backstop_data/engine_scripts',
        html_report: 'test/backstop_data/html_report',
        ci_report: 'test/backstop_data/ci_report'
    },
    // ['CI', 'browser']
    report: ['CI'],
    engine: 'puppeteer',
    engineOptions: {
        args: ['--no-sandbox']
    },
    asyncCaptureLimit: 5,
    asyncCompareLimit: 50,
    debug: false,
    debugWindow: false
};

function createScenariosFromConfig(sections) {
    const BLACK_LIST = ['GradientText', 'Modal', 'Шрифты'];

    return sections
        .reduce((scenarios, section) => {
            if (section.components) {
                scenarios = scenarios.concat(
                    section.components.map(component => {
                        const [origin, name] = /\/([a-z]+)\.tsx/gi.exec(component);

                        return buildScenario({
                            type: 'component',
                            name: section.name,
                            component: name
                        });
                    })
                );
            } else {
                scenarios.push(
                    buildScenario({
                        type: 'content',
                        name: section.name,
                        component: section.name
                    })
                );
            }

            return scenarios;
        }, [])
        .filter(scenario => !BLACK_LIST.includes(scenario.component));
}

function buildScenario(item) {
    const isComponent = item.type === 'component';

    return {
        component: item.component,
        label: `${item.name} - ${item.component}`,
        url: './gh-pages/index.html',
        removeSelectors: [],
        onReadyScript: '',
        clickSelectors: [`a[href$="#/${encodeURI(item.name)}"]`, `a[href$="#!/${encodeURI(item.component)}"]`],
        hideSelectors: ['.amber-button_loading', 'button[name="rsg-code-editor"]'],
        postInteractionWait: 400,
        selectors:
            isComponent
                ? [`div[data-testid=${item.component}-container] > article div[data-preview=${item.component}]`]
                : [`div[data-preview=${item.component}]`],
        selectorExpansion: !isComponent,
        misMatchThreshold: 0.2
    };
}

module.exports = config;
