from copy import deepcopy

from traffic_madness.car.lane_switching_car import LaneSwitchingCar
from traffic_madness.car.simple_car import SimpleCar
from traffic_madness.track import Track
from traffic_madness.track.trackbucket import TrackBucket
from traffic_madness.config import Config

class MultiLaneTrack(Track):
    def __init__(self, speed_limit, track_length, num_lanes, max_num_cars):
        self.speed_limit = speed_limit
        self.track_length = track_length
        self.num_lanes = num_lanes
        self.max_num_cars = max_num_cars
        self.cars = None

        self.buffer_length = 3

        self.reset()

    def reset(self):
        config = Config()
        """Puts the track in its initial state"""
        self.cars = TrackBucket(track_length=self.track_length,
                                bucket_length=config.bucket_length,
                                num_lanes=self.num_lanes)
        new_car = LaneSwitchingCar(position=0,
                                   velocity=self.speed_limit,
                                   lane=0)
        self.cars.add_car(new_car)

    def update(self):
        """Performs a time step update of the entire track"""

        for car in self.cars.get_all_cars():
            old_position = car.position
            nearby_cars = self.cars.get_nearby_cars(position=car.position)
            nearby_cars[car.lane].remove(car)
            car.update(self.speed_limit, nearby_cars)
            # Check if we need to wrap the car (periodic boundary)
            if car.position >= self.track_length:
                car.position -= self.track_length
            # Inform the car tracker that the car has moved
            self.cars.car_has_moved(car=car, old_position=old_position)

        if self.cars.get_num_cars() < self.max_num_cars:
            # self.try_to_spawn_car()
            self.try_to_spawn_car_single_lane(lane=0)

    def try_to_spawn_car_single_lane(self, lane):
        # Check if there is room to spawn a new car
        back_cars = self.cars.get_nearby_cars(position=50)
        cars = back_cars[lane]
        if any([abs(car.position - self.track_length) < self.buffer_length for
                car in cars]):
            return
        new_car = LaneSwitchingCar(position=50,
                                   velocity=self.speed_limit,
                                   lane=lane)
        self.cars.add_car(new_car)

    def try_to_spawn_car(self):
        # Check if there is room to spawn a new car
        back_cars = self.cars.get_nearby_cars(position=0)
        for lane, cars in enumerate(back_cars):
            if any([abs(car.position - self.track_length) < self.buffer_length
                    for car in cars]):
                continue
            new_car = LaneSwitchingCar(position=0,
                                       velocity=self.speed_limit,
                                       lane=lane)
            self.cars.add_car(new_car)

    def get_all_cars(self):
        """Returns a list of all the car positions"""
        return self.cars.get_all_cars()
