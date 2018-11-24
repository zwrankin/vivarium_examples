import pandas as pd
from scipy import spatial
from sklearn.neighbors import KNeighborsClassifier

class Flock:

    configuration_defaults = {
        'neighbors': {
            'radius': 10
        }
    }

    def setup(self, builder):
        self.radius = builder.configuration.neighbors.radius

        builder.event.register_listener('time_step', self.on_time_step, priority=0)
        self.population_view = builder.population.get_view(['x', 'y', 'vx', 'vy'])

    def on_time_step(self, event):
        pop = self.population_view.get(event.index)

        self._neighbors = pd.Series([[]] * len(pop), index=pop.index)

        tree = spatial.KDTree(pop)

        # Iterate over each pair of simulates that are close together.
        for boid_1, boid_2 in tree.query_pairs(self.radius):
            # .iloc is used because query_pairs uses 0,1,... indexing instead of pandas.index
            self._neighbors.iloc[boid_1].append(self._neighbors.index[boid_2])
            self._neighbors.iloc[boid_2].append(self._neighbors.index[boid_1])

        for i in event.index:
            neighbors = self._neighbors[i]
            # RULE 1: Match velocity
            pop.iloc[i].vx += 0.1 * pop.iloc[neighbors].vx.mean()
            pop.iloc[i].vy += 0.1 * pop.iloc[neighbors].vy.mean()

            # RULE 2: velocity toward center of mass
            pop.iloc[i].vx += 0.1 * (pop.iloc[neighbors].x.mean() - pop.iloc[i].x)
            pop.iloc[i].vy += 0.1 * (pop.iloc[neighbors].y.mean() - pop.iloc[i].y)

        self.population_view.update(pop)


class FlockKMeans:
    configuration_defaults = {
        'neighbors': {
            'n': 5
        }
    }

    def setup(self, builder):
        self.n_neighbors = builder.configuration.neighbors.n_neighbors
        self.knn = KNeighborsClassifier(self.n_neighbors, weights='distance')
        columns_created = ['cluster']
        builder.population.initializes_simulants(self.on_initialize_simulants, columns_created)
        builder.event.register_listener('time_step', self.on_time_step, priority=0)
        self.population_view = builder.population.get_view(['x', 'y', 'vx', 'vy'])

    def on_initialize_simulants(self, pop_data):
        pop = self.population_view.get(event.index)
        pop['cluster'] = self.knn.fit_transform(pop[['x', 'y']])
        self.population_view.update(pop)

    def on_time_step(self, event):
        pop = self.population_view.get(event.index)

        pop['cluster'] = self.knn.fit_transform(pop[['x', 'y']])
        clusters = pop.groupby('cluster')[['x', 'y', 'vx', 'vy']].mean()

        # RULE 2: velocity toward center of mass
        pop['vx'] = pop.apply(lambda row: 0.5 * row.vx + 0.5 * (row.x - clusters.iloc[row.cluster].x))
        pop['vy'] = pop.apply(lambda row: 0.5 * row.vy + 0.5 * (row.y - clusters.iloc[row.cluster].y))

        # RULE 1: Match velocity
        pop['vx'] = pop.apply(lambda row: 0.8 * row.vx + 0.2 * clusters.iloc[row.cluster].vx)
        pop['vy'] = pop.apply(lambda row: 0.8 * row.vy + 0.2 * clusters.iloc[row.cluster].vy)

        self.population_view.update(pop)