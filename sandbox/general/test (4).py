# -*- coding: utf-8 -*-
from sandbox.projects.sport_wizard.pushes.lib.push_processor import PushProcessor
from sport_api_fetcher import get_WC2018_events
from sport_api_fetcher import get_match_info
from pushes_wc2018 import filter_event_info
from pushes_wc2018 import generate_pushes
from pushes_wc2018 import WC2018PushSender
from pushes_wc2018 import mongoConfig


def main():
    logFilename = "events.log"
    oauthKey = ""
    mainTaskInstance = PushProcessor(get_WC2018_events, get_match_info, filter_event_info, generate_pushes, WC2018PushSender(oauthKey), mongoConfig['dev'])  # , logFilename)
    mainTaskInstance.main()


if __name__ == "__main__":
    main()
