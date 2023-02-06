export const prepareDomStylesForTests = () => {
  const disableAnimation = `
        body, body *, body *:after, body *:before,
        body[class], body[class] *, body[class] *:after, body[class] *:before {
            animation-duration: 0s !important;
            transition-duration: 0s !important;
            transition-delay: 0s !important;
        }
    `

  const disableScrollBars = `
        *::-webkit-scrollbar {
            display: none !important;
        }
    `

  const css = [disableAnimation, disableScrollBars].join('')
  const style = document.createElement('style')
  style.innerHTML = css
  document.head.appendChild(style)
}
