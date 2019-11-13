# Copyright 2019 Robert Bosch GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from tracetools_test.case import TraceTestCase


class TestIntra(TraceTestCase):

    def __init__(self, *args) -> None:
        super().__init__(
            *args,
            session_name_prefix='session-test-intra',
            events_ros=[
                'ros2:rcl_subscription_init',
                'ros2:rclcpp_subscription_callback_added',
                'ros2:callback_start',
                'ros2:callback_end',
            ],
            nodes=['test_intra']
        )

    def test_all(self):
        # Check events order as set (e.g. node_init before pub_init)
        self.assertEventsOrderSet(self._events_ros)

        # Check sub_init
        sub_init_events = self.get_events_with_name('ros2:rcl_subscription_init')
        sub_init_normal_events = self.get_events_with_field_value(
            'topic_name',
            '/the_topic',
            sub_init_events)
        self.assertNumEventsEqual(
            sub_init_normal_events,
            1,
            'none or more than 1 sub init event')

        # Get subscription handle
        sub_init_normal_event = sub_init_normal_events[0]
        sub_handle_intra = self.get_field(sub_init_normal_event, 'subscription_handle')

        # Get corresponding callback handle
        # Callback handle
        callback_added_events = self.get_events_with_field_value(
            'subscription_handle',
            sub_handle_intra,
            self.get_events_with_name(
                'ros2:rclcpp_subscription_callback_added'))
        self.assertNumEventsEqual(
            callback_added_events,
            1,
            'none or more than 1 callback added event')
        callback_added_event = callback_added_events[0]
        callback_handle = self.get_field(callback_added_event, 'callback')

        # Get corresponding callback start/end pairs
        start_events = self.get_events_with_name('ros2:callback_start')
        end_events = self.get_events_with_name('ros2:callback_end')
        # Should have at least one start:end pair
        self.assertNumEventsGreaterEqual(
            start_events,
            1,
            'does not have at least 1 callback start event')
        self.assertNumEventsGreaterEqual(
            end_events,
            1,
            'does not have at least 1 callback end event')
        start_events_intra = self.get_events_with_field_value(
            'callback',
            callback_handle,
            start_events)
        end_events_intra = self.get_events_with_field_value(
            'callback',
            callback_handle,
            end_events)
        self.assertNumEventsGreaterEqual(
            start_events_intra,
            1,
            'no intra start event')
        self.assertNumEventsGreaterEqual(
            end_events_intra,
            1,
            'no intra end event')

        # Check is_intra_process field value
        start_event_intra = start_events_intra[0]
        self.assertFieldEquals(
            start_event_intra,
            'is_intra_process',
            1,
            'is_intra_process field value not valid for intra callback')


if __name__ == '__main__':
    unittest.main()
