from sandbox.projects.release_machine.components.config_core.jg.cube.lib.metrics import SearchLaunchMetrics


class NoapacheLaunchMetrics(SearchLaunchMetrics):
    @property
    def input_override(self):
        return {
            "sample_beta": "upper-hamster.hamster",
            "sla_project": "aa8286386850f0df016874cc48882d44",
            "scraper_over_yt_pool": "upper_{}_priemka".format(self._search_subtype),
            "run_findurl": self._search_subtype != "web",
        }
