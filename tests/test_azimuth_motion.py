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

import asynctest
import logging
import math

from lsst.ts.MTDome.mock_llc.mock_motion import AzimuthMotion
from lsst.ts.idl.enums.MTDome import MotionState

logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG
)

_MAX_SPEED = math.radians(4.0)
_start_tai = 10001.0


class AzimuthMotionTestCase(asynctest.TestCase):
    async def prepare_azimuth_motion(self, start_position, max_speed, start_tai):
        """Prepare the AzimuthMotion for future commands.

        Parameters
        ----------
        start_position: `float`
            The start position of the azimuth motion.
        max_speed: `float`
            The maximum allowed speed.
        start_tai: `float`
            The start TAI time.
        """
        self.azimuth_motion = AzimuthMotion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )

    async def verify_azimuth_motion_duration(
        self,
        start_tai,
        target_position,
        crawl_velocity,
        expected_duration,
        motion_state,
    ):
        """Verify that the AzimuthMotion computes the correct
        duration.

        Parameters
        ----------
        start_tai: `float`
            The TAI time at which the command was issued.
        target_position: `float`
            The target position.
        crawl_velocity: `float`
            The crawl velocity after the motion.
        expected_duration: `float`
            The expected duration.
        motion_state: `MotionState`
            The commanded MotionState.
        """
        duration = self.azimuth_motion.set_target_position_and_velocity(
            start_tai=start_tai,
            end_position=target_position,
            crawl_velocity=crawl_velocity,
            motion_state=motion_state,
        )
        self.assertAlmostEqual(expected_duration, duration)

    async def verify_azimuth_motion(
        self, tai, expected_position, expected_velocity, expected_motion_state
    ):
        """Verify the position of the AzimuthMotion at the given TAI
        time.

        Parameters
        ----------
        tai: `float`
            The TAI time to compute the position for.
        expected_position: `float`
            The expected position at the given TAI time.
        expected_velocity: `float`
            The expected velocity at the given TAI time.
        expected_motion_state: `float`
            The expected motion state at the given TAI time.
        """
        (
            position,
            velocity,
            motion_state,
        ) = self.azimuth_motion.get_position_velocity_and_motion_state(tai)
        self.assertAlmostEqual(expected_position, position)
        self.assertAlmostEqual(expected_velocity, velocity)
        self.assertEqual(expected_motion_state, motion_state)

    async def test_move_zero_ten_pos(self):
        """Test the AzimuthMotion when moving from position 0 to
        position 10 degrees and then crawl in positive direction.
        """
        start_position = 0.0
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = math.radians(10.0)
        crawl_velocity = math.radians(0.1)
        expected_duration = (target_position - start_position) / max_speed
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        await self.verify_azimuth_motion_duration(
            start_tai=start_tai,
            target_position=target_position,
            crawl_velocity=crawl_velocity,
            expected_duration=expected_duration,
            motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 1.0,
            expected_position=math.radians(4.0),
            expected_velocity=_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 2.0,
            expected_position=math.radians(8.0),
            expected_velocity=_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 2.5,
            expected_position=math.radians(10.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 4.0,
            expected_position=math.radians(10.15),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )

    async def test_move_zero_ten_neg(self):
        """Test the AzimuthMotion when moving from position 0 to
        position 10 degrees and then crawl in negative direction.
        """
        start_position = 0.0
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = math.radians(10.0)
        crawl_velocity = math.radians(-0.1)
        expected_duration = (target_position - start_position) / max_speed
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        await self.verify_azimuth_motion_duration(
            start_tai=start_tai,
            target_position=target_position,
            crawl_velocity=crawl_velocity,
            expected_duration=expected_duration,
            motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 1.0,
            expected_position=math.radians(4.0),
            expected_velocity=_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 2.0,
            expected_position=math.radians(8.0),
            expected_velocity=_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 2.5,
            expected_position=math.radians(10.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 4.0,
            expected_position=math.radians(9.85),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )

    async def test_move_ten_zero_pos(self):
        """Test the AzimuthMotion when moving from position 10 to
        position 0 degrees and then crawl in positive direction.
        """
        start_position = math.radians(10.0)
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = 0.0
        crawl_velocity = math.radians(0.1)
        expected_duration = math.fabs((target_position - start_position) / max_speed)
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        await self.verify_azimuth_motion_duration(
            start_tai=start_tai,
            target_position=target_position,
            crawl_velocity=crawl_velocity,
            expected_duration=expected_duration,
            motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 1.0,
            expected_position=math.radians(6.0),
            expected_velocity=-_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 2.0,
            expected_position=math.radians(2.0),
            expected_velocity=-_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 2.5,
            expected_position=math.radians(0.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 4.0,
            expected_position=math.radians(0.15),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )

    async def test_move_ten_zero_neg(self):
        """Test the AzimuthMotion when moving from position 10 to
        position 0 degrees and then crawl in negative direction.
        """
        start_position = math.radians(10.0)
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = 0.0
        crawl_velocity = math.radians(-0.1)
        expected_duration = math.fabs((target_position - start_position) / max_speed)
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        await self.verify_azimuth_motion_duration(
            start_tai=start_tai,
            target_position=target_position,
            crawl_velocity=crawl_velocity,
            expected_duration=expected_duration,
            motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 1.0,
            expected_position=math.radians(6.0),
            expected_velocity=-_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 2.0,
            expected_position=math.radians(2.0),
            expected_velocity=-_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 2.5,
            expected_position=math.radians(0.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 4.0,
            expected_position=math.radians(359.85),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )

    async def test_move_ten_threefifty_pos(self):
        """Test the AzimuthMotion when moving from position 10 to
        position 350 degrees then crawl in positive direction.
        """
        start_position = math.radians(10.0)
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = math.radians(350.0)
        crawl_velocity = math.radians(0.1)
        expected_duration = math.fabs(
            (target_position - start_position - 2 * math.pi) / max_speed
        )
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        await self.verify_azimuth_motion_duration(
            start_tai=start_tai,
            target_position=target_position,
            crawl_velocity=crawl_velocity,
            expected_duration=expected_duration,
            motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 1.0,
            expected_position=math.radians(6.0),
            expected_velocity=-_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 2.0,
            expected_position=math.radians(2.0),
            expected_velocity=-_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 3.0,
            expected_position=math.radians(358.0),
            expected_velocity=-_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 5.0,
            expected_position=math.radians(350.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 6.0,
            expected_position=math.radians(350.1),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )

    async def test_move_ten_threefifty_neg(self):
        """Test the AzimuthMotion when moving from position 10 to
        position 350 degrees then crawl in negative direction.
        """
        start_position = math.radians(10.0)
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = math.radians(350.0)
        crawl_velocity = math.radians(-0.1)
        expected_duration = math.fabs(
            (target_position - start_position - 2 * math.pi) / max_speed
        )
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        await self.verify_azimuth_motion_duration(
            start_tai=start_tai,
            target_position=target_position,
            crawl_velocity=crawl_velocity,
            expected_duration=expected_duration,
            motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 1.0,
            expected_position=math.radians(6.0),
            expected_velocity=-_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 2.0,
            expected_position=math.radians(2.0),
            expected_velocity=-_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 3.0,
            expected_position=math.radians(358.0),
            expected_velocity=-_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 5.0,
            expected_position=math.radians(350.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 6.0,
            expected_position=math.radians(349.9),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )

    async def test_move_threefifty_ten_pos(self):
        """Test the AzimuthMotion when moving from position 10 to
        position 350 degrees then crawl in positive direction.
        """
        start_position = math.radians(350.0)
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = math.radians(10.0)
        crawl_velocity = math.radians(0.1)
        expected_duration = math.fabs(
            (target_position - start_position + 2 * math.pi) / max_speed
        )
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        await self.verify_azimuth_motion_duration(
            start_tai=start_tai,
            target_position=target_position,
            crawl_velocity=crawl_velocity,
            expected_duration=expected_duration,
            motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 1.0,
            expected_position=math.radians(354.0),
            expected_velocity=_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 2.0,
            expected_position=math.radians(358.0),
            expected_velocity=_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 3.0,
            expected_position=math.radians(2.0),
            expected_velocity=_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 5.0,
            expected_position=math.radians(10.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 6.0,
            expected_position=math.radians(10.1),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )

    async def test_move_threefifty_ten_neg(self):
        """Test the AzimuthMotion when moving from position 10 to
        position 350 degrees then crawl in negative direction.
        """
        start_position = math.radians(350.0)
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = math.radians(10.0)
        crawl_velocity = math.radians(-0.1)
        expected_duration = math.fabs(
            (target_position - start_position + 2 * math.pi) / max_speed
        )
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        await self.verify_azimuth_motion_duration(
            start_tai=start_tai,
            target_position=target_position,
            crawl_velocity=crawl_velocity,
            expected_duration=expected_duration,
            motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 1.0,
            expected_position=math.radians(354.0),
            expected_velocity=_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 2.0,
            expected_position=math.radians(358.0),
            expected_velocity=_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 3.0,
            expected_position=math.radians(2.0),
            expected_velocity=_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 5.0,
            expected_position=math.radians(10.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 6.0,
            expected_position=math.radians(9.9),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )

    async def test_crawl_pos(self):
        """Test the AzimuthMotion when crawling in a positive
        direction while crossing the 0/360 boundary. It should pass the
        target position and keep on crawling
        """
        start_position = math.radians(350.0)
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = math.radians(10.0)
        crawl_velocity = math.radians(1.0)
        expected_duration = 0.0
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        await self.verify_azimuth_motion_duration(
            start_tai=start_tai,
            target_position=target_position,
            crawl_velocity=crawl_velocity,
            expected_duration=expected_duration,
            motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 1.0,
            expected_position=math.radians(351.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 2.0,
            expected_position=math.radians(352.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 10.0,
            expected_position=math.radians(0.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 11.0,
            expected_position=math.radians(1.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 20.0,
            expected_position=math.radians(10.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 21.0,
            expected_position=math.radians(11.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )

    async def test_crawl_neg(self):
        """Test the AzimuthMotion when crawling in a positive
        direction while crossing the 0/360 boundary. It should pass the
        target position and keep on crawling
        """
        start_position = math.radians(10.0)
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = math.radians(350.0)
        crawl_velocity = math.radians(-1.0)
        expected_duration = 0.0
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        await self.verify_azimuth_motion_duration(
            start_tai=start_tai,
            target_position=target_position,
            crawl_velocity=crawl_velocity,
            expected_duration=expected_duration,
            motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 1.0,
            expected_position=math.radians(9.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 2.0,
            expected_position=math.radians(8.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 10.0,
            expected_position=math.radians(0.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 11.0,
            expected_position=math.radians(359.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 20.0,
            expected_position=math.radians(350.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 21.0,
            expected_position=math.radians(349.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )

    async def test_stop_from_moving(self):
        """Test the AzimuthMotion when moving from position 0 to
        position 10 and getting stopped while moving.
        """
        start_position = 0.0
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = math.radians(10.0)
        crawl_velocity = 0
        expected_duration = (target_position - start_position) / max_speed
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        await self.verify_azimuth_motion_duration(
            start_tai=start_tai,
            target_position=target_position,
            crawl_velocity=crawl_velocity,
            expected_duration=expected_duration,
            motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 1.0,
            expected_position=math.radians(4.0),
            expected_velocity=_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        self.azimuth_motion.stop(start_tai=_start_tai + 2.0)
        await self.verify_azimuth_motion(
            tai=_start_tai + 3.0,
            expected_position=math.radians(8.0),
            expected_velocity=0,
            expected_motion_state=MotionState.STOPPED,
        )

    async def test_stop_from_crawling_after_moving(self):
        """Test the AzimuthMotion when moving from position 0 to
        position 10, start crawling and then getting stopped while crawling.
        """
        start_position = 0.0
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = math.radians(10.0)
        crawl_velocity = math.radians(0.1)
        expected_duration = (target_position - start_position) / max_speed
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        await self.verify_azimuth_motion_duration(
            start_tai=start_tai,
            target_position=target_position,
            crawl_velocity=crawl_velocity,
            expected_duration=expected_duration,
            motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 1.0,
            expected_position=math.radians(4.0),
            expected_velocity=_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 3.0,
            expected_position=math.radians(10.05),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        self.azimuth_motion.stop(start_tai=_start_tai + 4.0)
        await self.verify_azimuth_motion(
            tai=_start_tai + 5.0,
            expected_position=math.radians(10.15),
            expected_velocity=0,
            expected_motion_state=MotionState.STOPPED,
        )

    async def test_stop_from_crawling(self):
        """Test the AzimuthMotion when crawling and then getting
        stopped.
        """
        start_position = math.radians(10.0)
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = math.radians(10.0)
        crawl_velocity = math.radians(1.0)
        expected_duration = 0.0
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        await self.verify_azimuth_motion_duration(
            start_tai=start_tai,
            target_position=target_position,
            crawl_velocity=crawl_velocity,
            expected_duration=expected_duration,
            motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 1.0,
            expected_position=math.radians(11.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        self.azimuth_motion.stop(start_tai=_start_tai + 4.0)
        await self.verify_azimuth_motion(
            tai=_start_tai + 5.0,
            expected_position=math.radians(14.0),
            expected_velocity=0,
            expected_motion_state=MotionState.STOPPED,
        )

    async def test_park_from_moving(self):
        """Test the AzimuthMotion when moving from position 0 to
        position 10 and getting parked while moving.
        """
        start_position = 0.0
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = math.radians(10.0)
        crawl_velocity = 0
        expected_duration = (target_position - start_position) / max_speed
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        await self.verify_azimuth_motion_duration(
            start_tai=start_tai,
            target_position=target_position,
            crawl_velocity=crawl_velocity,
            expected_duration=expected_duration,
            motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 1.0,
            expected_position=math.radians(4.0),
            expected_velocity=_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        self.azimuth_motion.park(start_tai=_start_tai + 2.0)
        await self.verify_azimuth_motion(
            tai=_start_tai + 3.0,
            expected_position=math.radians(4.0),
            expected_velocity=-_MAX_SPEED,
            expected_motion_state=MotionState.PARKING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 4.0,
            expected_position=math.radians(0.0),
            expected_velocity=0,
            expected_motion_state=MotionState.PARKED,
        )

    async def test_park_from_crawling_after_moving(self):
        """Test the AzimuthMotion when moving from position 0 to
        position 10, start crawling and then getting parked while crawling.
        """
        start_position = 0.0
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = math.radians(10.0)
        crawl_velocity = math.radians(0.1)
        expected_duration = (target_position - start_position) / max_speed
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        await self.verify_azimuth_motion_duration(
            start_tai=start_tai,
            target_position=target_position,
            crawl_velocity=crawl_velocity,
            expected_duration=expected_duration,
            motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 1.0,
            expected_position=math.radians(4.0),
            expected_velocity=_MAX_SPEED,
            expected_motion_state=MotionState.MOVING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 3.0,
            expected_position=math.radians(10.05),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        self.azimuth_motion.park(start_tai=_start_tai + 4.0)
        await self.verify_azimuth_motion(
            tai=_start_tai + 5.0,
            expected_position=math.radians(6.15),
            expected_velocity=-_MAX_SPEED,
            expected_motion_state=MotionState.PARKING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 6.0,
            expected_position=math.radians(2.15),
            expected_velocity=-_MAX_SPEED,
            expected_motion_state=MotionState.PARKING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 7.0,
            expected_position=math.radians(0.0),
            expected_velocity=0,
            expected_motion_state=MotionState.PARKED,
        )

    async def test_park_from_crawling(self):
        """Test the AzimuthMotion when crawling and then getting
        parked.
        """
        start_position = math.radians(10.0)
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = math.radians(10.0)
        crawl_velocity = math.radians(1.0)
        expected_duration = 0.0
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        await self.verify_azimuth_motion_duration(
            start_tai=start_tai,
            target_position=target_position,
            crawl_velocity=crawl_velocity,
            expected_duration=expected_duration,
            motion_state=MotionState.CRAWLING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 1.0,
            expected_position=math.radians(11.0),
            expected_velocity=crawl_velocity,
            expected_motion_state=MotionState.CRAWLING,
        )
        self.azimuth_motion.park(start_tai=_start_tai + 4.0)
        await self.verify_azimuth_motion(
            tai=_start_tai + 5.0,
            expected_position=math.radians(10.0),
            expected_velocity=-_MAX_SPEED,
            expected_motion_state=MotionState.PARKING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 6.0,
            expected_position=math.radians(6.0),
            expected_velocity=-_MAX_SPEED,
            expected_motion_state=MotionState.PARKING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 7.0,
            expected_position=math.radians(2.0),
            expected_velocity=-_MAX_SPEED,
            expected_motion_state=MotionState.PARKING,
        )
        await self.verify_azimuth_motion(
            tai=_start_tai + 8.0,
            expected_position=math.radians(0.0),
            expected_velocity=0,
            expected_motion_state=MotionState.PARKED,
        )

    async def test_too_high(self):
        """Test the AzimuthMotion when trying to crawl at a too high
        speed.
        """
        start_position = math.radians(10.0)
        start_tai = _start_tai
        max_speed = _MAX_SPEED
        target_position = math.radians(11.0)
        crawl_velocity = math.radians(5.0)
        expected_duration = 0.0
        await self.prepare_azimuth_motion(
            start_position=start_position, max_speed=max_speed, start_tai=start_tai,
        )
        try:
            await self.verify_azimuth_motion_duration(
                start_tai=start_tai,
                target_position=target_position,
                crawl_velocity=crawl_velocity,
                expected_duration=expected_duration,
                motion_state=MotionState.MOVING,
            )
            self.fail("Expected a ValueError.")
        except ValueError:
            pass
