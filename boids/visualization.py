import matplotlib.pyplot as plt
import os
import shutil
import imageio


def plot_birds(simulation, plot_velocity=False):
    width = simulation.configuration.location.width
    height = simulation.configuration.location.height
    pop = simulation.population.population

    plt.figure(figsize=[12, 12])
    plt.scatter(pop.x, pop.y, color=pop.color)
    if plot_velocity:
        plt.quiver(pop.x, pop.y, pop.vx, pop.vy, color=pop.color, width=0.002)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.axis([0, width, 0, height])
    plt.show()


color_map = {0: 'black', 1: 'red', 2: 'blue', 3: 'yellow', 4: 'green', 5: 'brown', 6: 'gray', 7: 'orange'}


class SaveFrames:
    """
    Save one frame per step, that can then be assembled into GIF
    This is a hack because MovieWriter doesn't seem to work on Windows
    :param fname: the repo within which frames will be saved
    :param plot_type: whether to plot color as cluster or infection
    """

    def __init__(self, fname, plot_type='infection'):
        self.fname = fname
        self.plot_type = plot_type
        self.step = 1
        self.path = f'images/{self.fname}'
        shutil.rmtree(self.path, ignore_errors=True)
        os.mkdir(self.path)

    def setup(self, builder):
        self.width = builder.configuration.location.width
        self.height = builder.configuration.location.height
        builder.event.register_listener('time_step',
                                        self.on_time_step)  # priority??? Before or after they actually move?
        builder.event.register_listener('simulation_end', self.save_movie)
        self.population_view = builder.population.get_view(['x', 'y', 'vx', 'vy', 'cluster', 'infected'])

    def on_time_step(self, event):
        pop = self.population_view.get(event.index)
        if self.plot_type == 'cluster':
            pop['color'] = pop.cluster.map(color_map)
        elif self.plot_type == 'infection':
            pop['color'] = pop.infected.map(color_map)
        else:
            raise AssertionError(f'{self.plot_type} not recognized')

        plt.clf()
        self.plot_boids(pop)

        plt.savefig(f'{self.path}/step_{self.step}.png')
        self.step += 1

    def plot_boids(self, pop):
        plt.figure(figsize=[12, 12])
        plt.scatter(pop.x, pop.y, color=pop.color)
        plt.quiver(pop.x, pop.y, pop.vx, pop.vy, color=pop.color, width=0.002)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.axis([0, self.width, 0, self.height])

    def save_movie(self, event):
        # FIXME - this doesn't work - here's a hack to turn frames into gif after sim
        # import imageio
        # image_directory = 'images/test'
        # images = [i for i in os.listdir(image_directory) if 'png' in i]
        # images = [f'step_{i}.png' for i in range(1, len(images) + 1)]
        # with imageio.get_writer(f'{image_directory}/movie.gif', mode='I', fps=2) as writer:
        #     for i in images:
        #         image = imageio.imread(f'{image_directory}/{i}', format='png')
        #         writer.append_data(image)

        images = [i for i in os.listdir(self.path) if 'png' in i]
        import pdb;
        pdb.set_trace()
        with imageio.get_writer(f'{self.path}/movie.gif', mode='I', fps=2) as writer:
            for i in images:
                image = imageio.imread(f'{self.path}/{i}', format='png')
                writer.append_data(image)

# with MovieWriter('flock.gif') as mw:
#     components = [Population(), Location(), Flock(), mw]
#     sim = setup_simulation(components)
#     sim.take_steps(20)
