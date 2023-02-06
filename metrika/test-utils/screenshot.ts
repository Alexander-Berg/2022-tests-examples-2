import { readFileSync } from 'fs';
import ReactDOMServer from 'react-dom/server';
import React from 'react';
import postcss from 'postcss';
import postcssNested from 'postcss-nested';

export async function makeScreenshot(
    component: React.ReactElement,
    options?: { width: number; height: number },
): Promise<void> {
    const { width = 256, height = 256 } = options ?? {};

    const [html, styles] = await getComponentMarkup(component);

    /*
        Snapshot is needed not to take a screenshot when the snapshot has not changed
        It checked in toMatchScreenshot function
     */
    expect(`${styles}\n${html}`).toMatchSnapshot();

    const markup = `
        <style>${styles}</style>
        <div>
            ${html}
        </div>
    `;

    await expect(markup).toMatchScreenshot({ width, height });
}

async function getComponentMarkup(
    component: React.ReactElement,
): Promise<[string, string]> {
    const html = ReactDOMServer.renderToStaticMarkup(component);
    const styles = await getComponentStyles();
    return [html, styles];
}

async function getComponentStyles(): Promise<string> {
    // All css file paths that are used in the component are written to the global variable using babel visitor
    const paths: string[] = window.includedCssFiles || [];
    let resultStyles = '';
    for (let i = 0; i < paths.length; i++) {
        const css = readFileSync(paths[i]);
        const result = await postcss([postcssNested]).process(css, {
            from: paths[i],
        });
        resultStyles += result.css;
    }
    return resultStyles;
}
