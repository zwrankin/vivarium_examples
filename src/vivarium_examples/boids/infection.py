import numpy as np
import pandas as pd
from scipy import spatial


class Infection:
    configuration_defaults = {
        'infection': {
            'radius': 100,
            'n_start': 1,
        }
    }

    def setup(self, builder):
        self.radius = builder.configuration.infection.radius
        self.n_start = builder.configuration.infection.n_start

        columns_created = ['infected']
        builder.population.initializes_simulants(self.on_initialize_simulants, columns_created)
        builder.event.register_listener('time_step', self.on_time_step)
        self.population_view = builder.population.get_view(['x', 'y'] + columns_created)

    def on_initialize_simulants(self, pop_data):

        infection = pd.DataFrame({
            'infected': 0,
        }, index=pop_data.index)
        idx = np.random.choice(pop_data.index, self.n_start)
        infection.loc[idx, 'infected'] = 1
        self.population_view.update(infection)

    def on_time_step(self, event):
        pop = self.population_view.get(event.index)

        infected0 = pop.loc[pop.infected == 1].index.tolist()

        tree = spatial.KDTree(pop[['x', 'y']])

        infected1 = []
        # Iterate over each pair of simulants that are close together.
        for boid_1, boid_2 in tree.query_pairs(self.radius):
            if any([boid_1 in infected0, boid_2 in infected0]):
                infected1 += [boid_1, boid_2]

        pop.loc[infected1, 'infected'] = 1

        self.population_view.update(pop)
