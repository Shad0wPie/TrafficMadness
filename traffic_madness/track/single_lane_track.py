from copy import deepcopy

from traffic_madness.car.simple_car import SimpleCar
from traffic_madness.track import Track


class SingleLaneTrack(Track):
    def __init__(self, speed_limit, track_length, max_num_cars):
        self.speed_limit = speed_limit
        self.track_length = track_length
        self.max_num_cars = max_num_cars
        self.cars = []

        # This is is the car that has the lowest position value
        self.back_car_index = None
        self.buffer_length = 3

        self.reset()

    def reset(self):
        """Puts the track in its initial state"""
        new_car = SimpleCar(0, velocity=self.speed_limit)
        self.cars = [new_car]
        self.back_car_index = 0

    def update(self):
        """Performs a time step update of the entire track"""
        for i, car in enumerate(self.cars):
            # Get nearby cars (and handle periodic boundary)
            if len(self.cars) > 1:
                next_car_ind = (i + 1) % len(self.cars)
                previous_car_ind = i - 1
                next_car = self.cars[next_car_ind]
                previous_car = self.cars[previous_car_ind]
                if next_car.position < car.position:
                    next_car = deepcopy(next_car)
                    next_car.position += self.track_length
                if previous_car.position > car.position:
                    previous_car = deepcopy(previous_car)
                    previous_car.position -= self.track_length
                nearby_cars = [previous_car, next_car]
            else:
                nearby_cars = []

            car.update(self.speed_limit, nearby_cars)

            # Check if we need to wrap the car (periodic boundary)
            if car.position >= self.track_length:
                car.position -= self.track_length
                self.back_car_index = i

        if len(self.cars) < self.max_num_cars:
            self.try_to_spawn_car()

    def try_to_spawn_car(self):
        # Check if there is room to spawn a new car
        back_car = self.cars[self.back_car_index]
        if back_car.position > self.buffer_length:
            new_car = SimpleCar(0, velocity=back_car.velocity, acceleration=1)
            # Insert it right before the current back car to keep the order
            # (back car index doesn't change)
            self.cars.insert(self.back_car_index, new_car)

    def get_all_cars(self):
        """Returns a list of all the car positions"""
        return self.cars
