# This file is part of ts_MTDome.
#
# Developed for the Vera Rubin Observatory Telescope and Site Systems.
# This product includes software developed by the Vera Rubin Observatory
# Project (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = ["ElevationMotion"]

import logging
import math

from .base_llc_motion import BaseLlcMotion
from lsst.ts.idl.enums.MTDome import MotionState
import lsst.ts.salobj as salobj


class ElevationMotion(BaseLlcMotion):
    """Simulator for the elevation motion of the light and wind screen of the
    MTDome.

    Parameters
    ----------
    start_position: `float`
        The initial position [rad].
    min_position: `float`
        The minimum allowed position [rad].
    max_position: `float`
        The maximum allowed position [rad].
    max_speed: `float`
        The maximum allowed speed [rad/s].
    start_tai: `float`
        The current TAI time, unix seconds. To  model the real dome, this
        should be the current time. However, for unit tests it can be
        convenient to use other values.

    Notes
    -----
    This simulator can either move the light and wind screen to a target
    position at maximum speed and stop, or crawl at the specified velocity. It
    handles the min_position and max_position boundaries by stopping there.
    When either moving or crawling, a new move or crawl command is handled and
    the elevation motion/crawl can be stopped. To "park" the light and wind
    screen, it needs to be moved to min_position.

    """

    def __init__(
        self, start_position, min_position, max_position, max_speed, start_tai
    ):
        super().__init__(
            start_position=start_position,
            min_position=min_position,
            max_position=max_position,
            max_speed=max_speed,
            start_tai=start_tai,
        )
        self.log = logging.getLogger("MockPointToPointActuator")

    def get_position_velocity_and_motion_state(self, tai):
        """Computes the position and `MotionState` for the given TAI time.

        Parameters
        ----------
        tai: `float`
            The TAI time, unix seconds, for which to compute the position. To
            model the real dome, this should be the current time. However, for
            unit tests it can be convenient to use other values.

        Returns
        -------
        position: `float`
            The position [rad] at the given TAI time, taking both the move
            (optional) and crawl velocities into account.
        velocity: `float`
            The velocity [rad/s] at the given TAI time.
        motion_state: `MotionState`
            The MotionState at the given TAI time.
        """
        if tai >= self._end_tai:
            if self._commanded_motion_state in [
                MotionState.STOPPING,
                MotionState.STOPPED,
                MotionState.MOVING,
            ]:
                motion_state = MotionState.STOPPED
                position = self._end_position
                velocity = 0
            else:
                diff_since_crawl_started = tai - self._end_tai
                position = (
                    self._start_position
                    + self._crawl_velocity * diff_since_crawl_started
                )
                motion_state = MotionState.CRAWLING
                velocity = self._crawl_velocity
                if position >= self._max_position:
                    position = self._max_position
                    motion_state = MotionState.STOPPED
                    velocity = 0
                elif position <= self._min_position:
                    position = self._min_position
                    motion_state = MotionState.STOPPED
                    velocity = 0
                if self._crawl_velocity == 0:
                    motion_state = MotionState.STOPPED
                    velocity = 0
        elif tai < self._start_tai:
            raise ValueError(
                f"Encountered TAI {tai} which is smaller than start TAI {self._start_tai}"
            )
        else:
            frac_time = (tai - self._start_tai) / (self._end_tai - self._start_tai)
            distance = self._get_distance()
            position = self._start_position + distance * frac_time
            velocity = self._max_speed
            if distance < 0:
                velocity = -self._max_speed
            if self._commanded_motion_state == MotionState.STOPPING:
                motion_state = MotionState.STOPPED
                velocity = 0
            else:
                motion_state = MotionState.MOVING

        position = salobj.angle_wrap_nonnegative(math.degrees(position)).rad
        return position, velocity, motion_state

    def stop(self, start_tai):
        """Stops the current motion instantaneously.

        Parameters
        ----------
        start_tai: `float`
            The TAI time, unix seconds, at which the command was issued. To
            model the real dome, this should be the current time. However, for
            unit tests it can be convenient to use other values.
        """
        position, velocity, motion_state = self.get_position_velocity_and_motion_state(
            tai=start_tai
        )
        self._start_tai = start_tai
        self._start_position = position
        self._end_position = position
        self._crawl_velocity = 0
        self._commanded_motion_state = MotionState.STOPPING

    def park(self, start_tai):
        """Not used for the elevation motion.

        Parameters
        ----------
        start_tai: `float`
            The TAI time, unix seconds, at which the command was issued. To
            model the real dome, this should be the current time. However, for
            unit tests it can be convenient to use other values.

        Raises
        ----------
        NotImplementedError:
            The Light and Wind Screen cannot be parked.
        """
        raise NotImplementedError("The Light and Wind Screen cannot be parked.")
