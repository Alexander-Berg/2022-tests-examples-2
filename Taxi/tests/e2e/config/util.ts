export function patchStyles() {
    const disableAnimation = `
        body, body *, body *:after, body *:before,
        body[class], body[class] *, body[class] *:after, body[class] *:before {
            -webkit-animation-duration: 0s !important;
            -moz-animation-duration: 0s !important;
            -ms-animation-duration: 0s !important;
            animation-duration: 0s !important;
            -webkit-transition-duration: 0s !important;
            -moz-transition-duration: 0s !important;
            -ms-transition-duration: 0s !important;
            transition-duration: 0s !important;
            -webkit-transition-delay: 0s !important;
            -moz-transition-delay: 0s !important;
            -ms-transition-delay: 0s !important;
            transition-delay: 0s !important;
        }
    `;

    const staticHeader = `
        [data-testid="header"] {
            position: static !important;
        }
    `;

    const menuWithoutShadows = `
        [data-testid="more-menu"] {
            box-shadow: none !important;
        }
    `;

    const disableScrollBars = `
        *::-webkit-scrollbar {
            display: none !important;
        }
    `;

    const css = [disableAnimation, staticHeader, disableScrollBars, menuWithoutShadows].join('');
    const style = document.createElement('style');
    style.innerHTML = css;
    document.head.appendChild(style);
}
