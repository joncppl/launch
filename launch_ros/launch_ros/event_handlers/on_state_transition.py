# Copyright 2018 Open Source Robotics Foundation, Inc.
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

"""Module for OnStateTransition class."""

from typing import Callable
from typing import List
from typing import Optional
from typing import Text
from typing import Tuple

from launch.event import Event
from launch.event_handler import EventHandler
from launch.launch_description_entity import LaunchDescriptionEntity
from launch.some_actions_type import SomeActionsType
from launch.some_substitutions_type import SomeSubstitutionsType

from ..actions import LifecycleNode
from ..events.lifecycle import StateTransition


class OnStateTransition(EventHandler):
    """Convenience class for handling a state transition in a lifecycle node."""

    def __init__(
        self,
        *,
        entities: SomeActionsType,
        target_lifecycle_node: LifecycleNode = None,
        transition: Optional[SomeSubstitutionsType] = None,
        start_state: Optional[SomeSubstitutionsType] = None,
        goal_state: Optional[SomeSubstitutionsType] = None,
        matcher: Optional[Callable[[Event], bool]] = None,
    ) -> None:
        """
        Constructor.

        There are several matching options, each of which is compared with the
        event and must match it to have the handler handle the event.
        Passing None for any of them will prevent that matching option from
        being considered (and therefore not required) when matching the event.

        If matcher is given, the other conditions are not considered.
        """
        if not isinstance(target_lifecycle_node, (LifecycleNode, type(None))):
            raise RuntimeError("OnStateTransition requires a 'LifecycleNode' action as the target")
        # Handle optional matcher argument.
        self.__custom_matcher = matcher
        if self.__custom_matcher is None:
            self.__custom_matcher = (
                lambda event: (
                    isinstance(event, StateTransition) and (
                        target_lifecycle_node is None or
                        event.action == target_lifecycle_node
                    ) and (
                        transition is None or
                        event.transition == transition
                    ) and (
                        start_state is None or
                        event.start_state == start_state
                    ) and (
                        goal_state is None or
                        event.goal_state == goal_state
                    )
                )
            )
        # Call parent init.
        super().__init__(
            matcher=self.__custom_matcher,
            entities=entities,
        )
        self.__target_lifecycle_node = target_lifecycle_node

    def describe(self) -> Tuple[Text, List[LaunchDescriptionEntity]]:
        """Return the description list with 0 being a string, and then LaunchDescriptionEntity's."""
        return (
            "OnStateTransition(matcher='{}', handler=<actions>)".format(self.matcher_description),
            self.entities,
        )

    @property
    def matcher_description(self):
        """Return the string description of the matcher."""
        return 'event == StateTransition and event.action == LifecycleNode({})'.format(
            hex(id(self.__target_lifecycle_node))
        )