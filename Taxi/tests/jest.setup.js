const JScreenshot = require('jest-screenshot');

const options = {
    pixelThresholdRelative: 0.01
}

JScreenshot.setupJestScreenshot(options);
