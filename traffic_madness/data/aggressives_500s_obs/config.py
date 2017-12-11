'''global configuration file for quickly accessing and tuning parameters
of the simulation'''
class Config():
    def __init__(self):
        self.timestep = 0.1
        self.equilibration = 100 # Set equilibration time
        self.observation = 500 # Set time for observation
        self.fps = 60
        # track properties
        self.aggressives = 1.0 # % of aggressive drivers
        self.passives = 0.0 # passive drivers
        self.lanes = 3
        self.speed_limit = 20
        self.track_length = 1000
        self.buckets = 20.0
        self.max_num_cars = 150
        self.buffer_length = 5
        self.bucket_length = self.track_length / self.buckets
        # car properties
        self.acceleration = 4.3
        self.deceleration = 5.5
        self.max_deceleration = 10.0
        self.aggressiveness = 1.2
        self.passiveness = 0.8
        self.safetymultiplier = 1.5
        self.car_length = 5.0
        self.min_distance = 5.0
        self.nice_cars = False
#        self.delay_buffer_length = 2
        self.reaction_time = 1.0 # Seconds between deacceleration