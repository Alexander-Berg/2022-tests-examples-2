declare namespace WebdriverIO {
  interface Browser {
    openPage: import('../commands/openPage').OpenPage
    addStyles: import('../commands/addStyles').AddStyles
    waitForElementAndClick: import('../commands/waitForElementAndClick').WaitForElementAndClick
    waitForElementDisplayed: import('../commands/waitForElementDisplayed').WaitForElementDisplayed
    waitForElementExists: import('../commands/waitForElementExists').WaitForElementExists
    waitForElementText: import('../commands/waitForElementText').WaitElementForText
    scrollToElementEdge: import('../commands/scrollToElementEdge').ScrollToElementEdge
    assertImage: import('../commands/assertImage').AssertImage
    scrollByElement: import('../commands/scrollByElement').ScrollByElement
    scrollToElement: import('../commands/scrollToElement').ScrollToElement
    setInnerWindowSize: import('../commands/setInnerWindowSize').SetInnerWindowSize
    waitForElementScrollReleased: import('../commands/waitForElementScrollReleased').WaitForElementScrollReleased
    typeText: import('../commands/typeText').TypeText
    assertUrlPathname: import('../commands/assertUrlPathname').AssertUrlPathname
    waitForImages: import('../commands/waitForImages').WaitForImages
  }
}
