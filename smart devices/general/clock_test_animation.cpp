#include "clock_test_animation.h"

namespace {

    int brightnessStep = 5;
    int iterationCount = 3;
    constexpr auto frameLength = std::chrono::milliseconds(20);

} // namespace

ClockTestAnimation::ClockTestAnimation(std::weak_ptr<ScLedController> clockLedController, bool infinite)
    : Animation(clockLedController)
    , clockLedController_(std::move(clockLedController))
    , infinite_(infinite)
{
}

void ClockTestAnimation::drawCurrentFrame() {
    if (!started_) {
        return;
    }

    auto frame = ScLedFrame::makeEmptyFrame();
    for (const auto& part : {"A", "B", "C", "D", "E", "F", "G", "PLUS", "MINUS", "DEGREE"}) {
        for (const auto& position : {"1", "2", "3", "4"}) {
            frame.elements[{part, position}] = currentBrightness_;
        }
    }
    frame.elements[{"MINUS", ""}] = frame.elements[{"DEGREE", ""}] = currentBrightness_;
    if (auto clockLedController = clockLedController_.lock()) {
        clockLedController->drawFrame(frame);
    }
}

void ClockTestAnimation::updateTime(Animation::TimePoint timePoint) {
    if (!started_) {
        return;
    }

    // simulate constant frame rate
    while (timePoint >= endOfFrame_) {
        updateBrightness();
        endOfFrame_ = endOfFrame_ + frameLength;
    }
}
void ClockTestAnimation::updateBrightness() {
    if (currentBrightness_ == 0) {
        ++counter_;
        currentBrightness_ = ScLedFrame::brightnessOn;
    } else if (currentBrightness_ < brightnessStep) {
        currentBrightness_ = 0;
    } else {
        currentBrightness_ -= brightnessStep;
    }
}

bool ClockTestAnimation::finished() const {
    return !infinite_ && counter_ >= iterationCount;
}

Animation::TimePoint ClockTestAnimation::getEndOfFrameTimePoint() const {
    return endOfFrame_;
}

std::string ClockTestAnimation::getName() const {
    return "ClockTestAnimation";
}

void ClockTestAnimation::resetAnimation() {
    counter_ = 0;
    currentBrightness_ = ScLedFrame::brightnessOn;
    started_ = false;
}

void ClockTestAnimation::startAnimationFrom(Animation::TimePoint timePoint) {
    if (started_) {
        return;
    }

    endOfFrame_ = timePoint + frameLength;
    started_ = true;
}

std::chrono::nanoseconds ClockTestAnimation::getLength() const {
    return frameLength * (ScLedFrame::brightnessOn / brightnessStep);
}
