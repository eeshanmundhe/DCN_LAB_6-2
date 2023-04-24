import sys
import os
import pytest
from fsm import StateError

sys.path.append(os.path.realpath(os.getcwd()))
from tcp_fsm import init_tcp_fsm, TransitionError

# ([transitions], expected state)
TEST_DATA = (
(["ACTIVE","SYNACK","FIN"],  "CLOSE_WAIT"),
(["PASSIVE",  "SYN","ACK"],  "ESTABLISHED"),
(["ACTIVE","SYNACK","FIN","CLOSE"],  "LAST_ACK"),
(["ACTIVE"],  "SYN_SENT"),
(["PASSIVE","SYN","ACK","CLOSE","SEND"],  "ERROR"),
(["PASSIVE",  "SYN","ACK",   "CLOSE"],  "FIN_WAIT_1"),
(["PASSIVE",  "SYN","ACK"],  "ESTABLISHED"),
(["PASSIVE",  "SYN"],  "SYN_RCVD"),
(["PASSIVE"],  "LISTEN"),
(["ACTIVE","CLOSE"],  "CLOSED"),
(["ACTIVE","SYN","CLOSE","FIN","ACK"],  "TIME_WAIT"),
(["ACTIVE","SYN","CLOSE","FIN","ACK","TIMEOUT"],  "CLOSED"),
(["SYN","ACK","CLOSE"],  "ERROR"),
(["ACTIVE","SYN","CLOSE","ACK"],  "FIN_WAIT_2"),
(["ACTIVE","SYNACK","FIN"],  "CLOSE_WAIT"),
(["ACTIVE","SYNACK","FIN","CLOSE"],  "LAST_ACK"),
(["ACTIVE"],  "SYN_SENT"),
(["PASSIVE","CLOSE"],  "CLOSED"),
(["ACTIVE","SYNACK","CLOSE"],  "FIN_WAIT_1"),
(["PASSIVE","SYN","ACK","PASSIVE"],  "ERROR"),
(["PASSIVE","SYN","ACK","CLOSE","ACK","FIN"],  "TIME_WAIT"),
(["PASSIVE","SYN","ACK","CLOSE","SYN"],  "ERROR"),
(["PASSIVE","CLOSE","SYN"],  "ERROR"),
(["PASSIVE","SYN","ACK","CLOSE"],  "FIN_WAIT_1"),
(["PASSIVE","SYN","ACK","CLOSE","FIN"],  "CLOSING"))

@pytest.mark.parametrize("transitions, expected_state", TEST_DATA)
def test_tcp_fsm(transitions, expected_state):
    assert_equals(transitions, expected_state)

    
def assert_equals(events, expected_state):
    tcp_fsm = init_tcp_fsm()
    current_event = events
    for i in range(len(current_event)):
        if i<0 :
            raise StateError()
    for event in events:
        try:
            tcp_fsm.transition(event)
        except TransitionError as err:
            if expected_state == "ERROR":
                return
            else:
                raise err
    assert tcp_fsm.current_state.name == expected_state, (events, expected_state)


