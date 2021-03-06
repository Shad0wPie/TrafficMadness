from traffic_madness.car import Car
from traffic_madness.config import Config


class LaneSwitchingCar(Car):
    def update(self, target_speed, nearby_cars):
        if self.stuck:
            return

        config = Config()
        # Cannot set to 0, else cars never brake

        dist_to_car_in_front, dist_to_car_in_back, car_in_front, car_in_back \
            = self._get_dist_to_front_and_back(nearby_cars)
        safety_distance = max(self.velocity * self.safetymultiplier,
                              self.min_distance)

        """
        Lane switching logic:
        cars generally switch lane when they are not driving at optimal
        velocity and the other lane has a higher velocity/no cars

        nice cars additionally switch to the right lane whenever it has
        space and the velocity is better or equal to the current velocity
        """
        switched = False
        if not switched and self.nice:
            if self.lane != 0:
                switched = self.attempt_lane_shift(nearby_cars,
                                                   safety_distance,
                                                   allow_left=False)
        if not switched and (dist_to_car_in_front < safety_distance and
                                     car_in_front.velocity < target_speed):
            switched = self.attempt_lane_shift(nearby_cars,
                                               safety_distance)
        if not switched and (dist_to_car_in_back < safety_distance and
                                     car_in_back.velocity >= self.velocity):
            switched = self.attempt_lane_shift(nearby_cars,
                                               safety_distance,
                                               prefer_right=True)

        # Update distances if we switched lanes
        if switched:
            dist_to_car_in_front, dist_to_car_in_back, car_in_front, \
            car_in_back = self._get_dist_to_front_and_back(nearby_cars)

        # Speed up to speed limit if no car in front
        if dist_to_car_in_front > safety_distance:
            if self.velocity < target_speed:
                self.velocity = \
                    min([self.velocity + self.acceleration * self.timestep,
                         target_speed])
        else:
            if self.velocity_factor and self.velocity < car_in_front.velocity:
                distance_part = 0
            else:
                distance_part = (1 - (dist_to_car_in_front / safety_distance)**2) * 2 
            velocity_part = self.velocity_factor * (self.velocity - car_in_front.velocity)
            deceleration = self.deceleration * (distance_part + velocity_part)
            deceleration = min(deceleration, config.max_deceleration)
            deceleration = max(-config.acceleration, deceleration)
            self.velocity = max(
                  0, self.velocity - deceleration * self.timestep)

        # self.delay_buffer.append(self.velocity)
        #        self.velocity = 0
        #        if (len(self.delay_buffer) > self.delay_buffer_length):
        #            self.velocity = self.delay_buffer.pop(0)

        # position is in the front of the car
        self.update_position(dist_to_car_in_front)

        assert self.velocity >= 0

    def update_position(self, distance_to_car_in_front):
        """ Updates the position of the car. If it reaches the 
            position of the car in front, the cars collide.
            Passing not allowed except for lane switching."""
        proposed_position = self.position + self.velocity * self.timestep
        # TODO(CHANGE THIS DANIEL): This should not be - own length,
        # send car instead
        crash_position = self.position + distance_to_car_in_front

        if proposed_position > crash_position and self.position >= \
              crash_position:
            # We stay at the same spot until car in front moves
            self.velocity = 0
            print("Car has crashed at {}".format(self.position))
        elif proposed_position > crash_position and self.position < \
              crash_position:
            self.position = crash_position
            self.velocity = 0
            print("Car has crashed at {}".format(self.position))
        else:
            self.position = proposed_position

    def _get_dist_to_front_and_back(self, nearby_cars, lane=None):
        if lane is None:
            lane = self.lane
        dist_to_car_in_front = float('inf')
        dist_to_car_in_back = float('inf')
        car_in_front = Car(float('inf'), float('inf'))
        car_in_back = Car(float('inf'), float('inf'))
        for car in nearby_cars[lane]:
            dist = car.position - self.position
            if dist > 0 and dist < dist_to_car_in_front:
                dist_to_car_in_front = dist
                car_in_front = car
            elif dist < 0 and abs(dist) < dist_to_car_in_back:
                dist_to_car_in_back = abs(dist)
                car_in_back = car
        dist_to_car_in_front -= car_in_front.length
        dist_to_car_in_back -= self.length
        return dist_to_car_in_front, dist_to_car_in_back, car_in_front, \
               car_in_back

    def attempt_lane_shift(self, nearby_cars, safety_distance,
                           prefer_right=True, allow_left=True,
                           allow_right=True):
        # Check lane shift
        allowed_lanes = []
        if allow_left and self.lane < len(nearby_cars) - 1:
            allowed_lanes.append(self.lane + 1)
        if allow_right and self.lane > 0:
            allowed_lanes.append(self.lane - 1)

        if prefer_right:
            allowed_lanes = reversed(allowed_lanes)

        for lane in allowed_lanes:
            if self.lane_is_safe(nearby_cars, lane, safety_distance):
                self.lane = lane
                return True
        return False

    def lane_is_safe(self, nearby_cars, lane, safety_distance):
        if not nearby_cars[lane]:
            return True

        dist_to_car_in_front, dist_to_car_in_back, car_in_front, car_in_back \
            = self._get_dist_to_front_and_back(nearby_cars, lane=lane)
        front_ok = (dist_to_car_in_front > safety_distance or
                    (car_in_front.velocity > self.velocity and
                     dist_to_car_in_front > self.min_distance))
        back_ok = (dist_to_car_in_back > safety_distance or
                   (car_in_back.velocity < self.velocity and
                    dist_to_car_in_back > self.min_distance))

        return front_ok and back_ok
