import numpy as np
import pandas as pd


class Location:
    configuration_defaults = {
        'location': {
            'max_velocity': 20,
            'width': 1000,  # Width of our field
            'height': 1000,  # Height of our field
        }
    }

    def setup(self, builder):
        self.width = builder.configuration.location.width
        self.height = builder.configuration.location.height
        self.max_velocity = builder.configuration.location.max_velocity

        columns_created = ['x', 'vx', 'y', 'vy']
        builder.population.initializes_simulants(self.on_create_simulants, columns_created)
        builder.event.register_listener('time_step', self.on_time_step)
        self.population_view = builder.population.get_view(columns_created)

    def on_create_simulants(self, pop_data):
        count = len(pop_data.index)
        # Start clustered in the center with small random velocities
        new_population = pd.DataFrame({
            'x': np.random.uniform(0, self.width, count),  # self.width * (0.4 + 0.2 * np.random.random(count)),
            'y': np.random.uniform(0, self.height, count),  # self.height * (0.4 + 0.2 * np.random.random(count)),
            'vx': self.max_velocity * np.random.randn(count),  # -0.5 + np.random.random(count),
            'vy': self.max_velocity * np.random.randn(count),  # -0.5 + np.random.random(count),
        }, index=pop_data.index)
        self.population_view.update(new_population)

    def on_time_step(self, event):
        pop = self.population_view.get(event.index)

        # Limit velocity
        pop.loc[pop.vx > self.max_velocity, 'vx'] = self.max_velocity
        pop.loc[pop.vx < -self.max_velocity, 'vx'] = -self.max_velocity
        pop.loc[pop.vy > self.max_velocity, 'vy'] = self.max_velocity
        pop.loc[pop.vy < -self.max_velocity, 'vy'] = -self.max_velocity

        pop['x'] = pop.apply(lambda row: self.move_boid(row.x, row.vx, self.width), axis=1)
        pop['vx'] = pop.apply(lambda row: self.avoid_wall(row.x, row.vx, self.width), axis=1)
        pop['y'] = pop.apply(lambda row: self.move_boid(row.y, row.vy, self.height), axis=1)
        pop['vy'] = pop.apply(lambda row: self.avoid_wall(row.y, row.vy, self.height), axis=1)

        self.population_view.update(pop)

    def move_boid(self, position, velocity, limit):
        if in_boundary(position, velocity, limit):
            return position + velocity
        else:
            return position

    def avoid_wall(self, position, velocity, limit):
        if in_boundary(position, velocity, limit):
            return velocity
        else:
            return velocity * -1


def in_boundary(position, velocity, limit):
    return (position + velocity < limit) & (position + velocity > 0)
