class InfectionObserver:
    """
    As the output.hdf table for a distributed run has only one row per run,
    this data needs to be saved in wide format
    For each step, it will have one column for infection prevalence, and one column for infection incidence
    """

    def __init__(self):
        self.step = 0
        self.data = {'prevalence_0': 0, 'incidence_0': 0}  # TODO - make it initial prevalence

    def setup(self, builder):
        self.population_view = builder.population.get_view(['infected'])
        builder.event.register_listener('collect_metrics', self.on_collect_metrics)
        builder.value.register_value_modifier('metrics', self.metrics)

    def on_collect_metrics(self, event):
        self.step += 1
        pop = self.population_view.get(event.index)
        prevalence = pop.infected.mean()  # TODO - should it be absolute or relative?
        incidence = prevalence - self.data[f'prevalence_{self.step - 1}']  # TODO - should it be the hazard?

        self.data[f'prevalence_{self.step}'] = prevalence
        self.data[f'incidence_{self.step}'] = incidence

    def metrics(self, index, metrics):
        # Recall that metrics is a dictionary
        for key in self.data.keys():
            value = self.data[key]
            metrics[key] = value

        return metrics
