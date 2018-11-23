class Location:

    configuration_defaults = {
        'location': {
            'width': 1000,   # Width of our field
            'height': 1000,  # Height of our field
        }
    }

    def setup(self, builder):
        self.width = builder.configuration.location.width
        self.height = builder.configuration.location.height

        columns_created = ['x', 'vx', 'y', 'vy']
        builder.population.initializes_simulants(self.on_create_simulants, columns_created)
        builder.event.register_listener('time_step', self.on_time_step)
        self.population_view = builder.population.get_view(columns_created)

    def on_create_simulants(self, pop_data):
        count = len(pop_data.index)
        # Start clustered in the center with small random velocities
        new_population = pd.DataFrame({
            'x': self.width * (0.4 + 0.2 * np.random.random(count)),
            'y': self.width * (0.4 + 0.2 * np.random.random(count)),
            'vx': 10 * np.random.randn(count),  # -0.5 + np.random.random(count),
            'vy': 10 * np.random.randn(count),  # -0.5 + np.random.random(count),
        }, index=pop_data.index)
        self.population_view.update(new_population)

    def on_time_step(self, event):
        pop = self.population_view.get(event.index)

        pop['x'] = pop.apply(lambda row: self.move_boid(row.x, row.vx, self.width), axis=1)
        pop['vx'] = pop.apply(lambda row: self.avoid_wall(row.x, row.vx, self.width), axis=1)
        pop['y'] = pop.apply(lambda row: self.move_boid(row.y, row.vy, self.height), axis=1)
        pop['vy'] = pop.apply(lambda row: self.avoid_wall(row.y, row.vy, self.height), axis=1)

        self.population_view.update(pop)
