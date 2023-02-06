import typing as tp

from . import base
from . import facets
from . import measures
from . import metrics_groups
from . import plots
from . import precomputes_tables
from . import responses


class Builders:
    def get_facets_builder(self) -> facets.FacetsBuilder:
        return facets.FacetsBuilder()

    def get_mg_config_builder(
            self,
    ) -> metrics_groups.MetricsGroupConfigBuilder:
        return metrics_groups.MetricsGroupConfigBuilder(
            self.get_facets_builder(),
        )

    def get_pt_schema_builder(
            self,
    ) -> precomputes_tables.PrecomputesTableSchemaBuilder:
        return precomputes_tables.PrecomputesTableSchemaBuilder()

    def get_pt_attributes_builder(
            self,
    ) -> precomputes_tables.PrecomputesTableAttributesBuilder:
        return precomputes_tables.PrecomputesTableAttributesBuilder()

    def get_measures_builder(
            self, revision_id: int, group_id: int, buckets_count: int,
    ) -> measures.MeasuresBuilder:
        return measures.MeasuresBuilder(revision_id, group_id, buckets_count)

    def get_response_builder(self, path: str) -> tp.Type[base.BaseBuilder]:
        return responses.find_builder(path)

    def get_plot_data_builder(self) -> plots.PlotDataBuilder:
        return plots.PlotDataBuilder()


__all__ = ['Builders']
