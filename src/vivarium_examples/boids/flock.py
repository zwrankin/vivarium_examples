import numpy as np
import pandas as pd
from scipy import spatial
from sklearn.cluster import KMeans


class Flock:
    """Component to make flocking behavior based on location and velocity of boids within set radius"""

    configuration_defaults = {
        'flock': {
            'radius': 10
        }
    }

    def setup(self, builder):
        self.radius = builder.configuration.flock.radius

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
    """
    Component to make flocking behavior based on location and velocity of boids of the cluster
    Clusters are determined using sklearn.cluster.Kmeans with n_clusters
    Note that cluster labels themselves are arbitrary and have no memory across time steps
    """

    configuration_defaults = {
        'flock': {
            'n_clusters': 8
        }
    }

    def setup(self, builder):
        self.n_clusters = builder.configuration.flock.n_clusters
        self.kmeans = KMeans(self.n_clusters, random_state=0)
        columns_created = ['cluster']
        builder.population.initializes_simulants(self.on_initialize_simulants, columns_created)
        builder.event.register_listener('time_step', self.on_time_step, priority=0)
        self.population_view = builder.population.get_view(['x', 'y', 'vx', 'vy'] + columns_created)

    def on_initialize_simulants(self, pop_data):
        # Can't seem to use other columns during initialization
        #         pop = self.population_view.get(pop_data.index)
        #         self.kmeans.fit(pop[['x', 'y']])
        #         pop['cluster'] = self.kmeans.labels_
        pop = pd.DataFrame({
            'cluster': [1] * len(pop_data.index),
        })
        self.population_view.update(pop)

    def on_time_step(self, event):
        pop = self.population_view.get(event.index)
        self.kmeans.fit(pop[['x', 'y']])
        pop['cluster'] = self.kmeans.labels_
        pop.cluster = pop.cluster.astype('int64')  # picky picky Vivarium
        clusters = pop.groupby('cluster')[['x', 'y', 'vx', 'vy']].mean()

        # RULE 2: velocity toward center of mass
        pop['vx'] = pop.apply(lambda row: 1 * row.vx + 0.05 * (clusters.iloc[int(row.cluster)].x - row.x),
                              axis=1)
        pop['vy'] = pop.apply(lambda row: 1 * row.vy + 0.05 * (clusters.iloc[int(row.cluster)].y - row.y),
                              axis=1)

        # RULE 1: Match velocity
        pop['vx'] = pop.apply(lambda row: 1 * row.vx + 0.1 * clusters.iloc[int(row.cluster)].vx,
                              axis=1)
        pop['vy'] = pop.apply(lambda row: 1 * row.vy + 0.1 * clusters.iloc[int(row.cluster)].vy,
                              axis=1)

        # RULE 3: give cluster some acceleration (for now, same for x and y)
        clusters['a'] = 5 * np.random.randn(self.n_clusters)
        pop['vx'] = pop.apply(lambda row: row.vx + clusters.iloc[int(row.cluster)].a, axis=1)
        pop['vy'] = pop.apply(lambda row: row.vy + clusters.iloc[int(row.cluster)].a, axis=1)

        self.population_view.update(pop)
