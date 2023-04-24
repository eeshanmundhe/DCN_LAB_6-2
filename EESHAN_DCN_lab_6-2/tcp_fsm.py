import sys
import os
sys.path.append(os.path.realpath(os.getcwd()))
from fsm import MealyMachine, State, TransitionError


VALID_TCP_EVENTS=[]
VALID_TCP_EVENTS.append("TIMEOUT")
VALID_TCP_EVENTS.append("SDATA")
VALID_TCP_EVENTS.append("RDATA")
VALID_TCP_EVENTS.append("FIN")
VALID_TCP_EVENTS.append("ACK")
VALID_TCP_EVENTS.append("SYNACK")
VALID_TCP_EVENTS.append("CLOSE")
VALID_TCP_EVENTS.append("SYN")
VALID_TCP_EVENTS.append("ACTIVE")
VALID_TCP_EVENTS.append("PASSIVE")


transition_outputs = {}
transition_outputs['n_out'] = '<n>'
transition_outputs['fin'] = '<fin>'
transition_outputs['ack']= '<ack>'
transition_outputs['syn_ack'] = '<syn-ack>'
transition_outputs['syn']     = '<syn>'

NONE    = u"Λ"

state_closed      = State("CLOSED", initial=True)
state_listen      = State("LISTEN")
state_syn_sent    = State("SYN_SENT")
state_syn_rcvd    = State("SYN_RCVD")
state_established = State("ESTABLISHED")
state_fin_wait_1  = State("FIN_WAIT_1")
state_fin_wait_2  = State("FIN_WAIT_2")
state_closing     = State("CLOSING")
state_time_wait   = State("TIME_WAIT")
state_close_wait  = State("CLOSE_WAIT")
state_last_ack    = State("LAST_ACK")

state_established.received_count = 0
state_established.sent_count     = 0

# Transitions
# <state name>[(<input>, <output>)] = <next state>
state_closed[("PASSIVE",    NONE)]    = state_listen
state_closed[("ACTIVE",     transition_outputs['syn'])]     = state_syn_sent
state_listen[("SYN",        transition_outputs['syn_ack'])] = state_syn_rcvd
state_listen[("CLOSE",      NONE)]    = state_closed
state_syn_sent[("CLOSE",    NONE)]    = state_closed
state_syn_sent[("SYN",      transition_outputs['syn_ack'])] = state_syn_rcvd
state_syn_sent[("SYNACK",   transition_outputs['ack'])]     = state_established
state_syn_rcvd[("ACK",      NONE)]    = state_established
state_syn_rcvd[("CLOSE",    transition_outputs['fin'])]     = state_fin_wait_1
state_established[("CLOSE", transition_outputs['fin'])]     = state_fin_wait_1
state_established[("FIN",   transition_outputs['ack'])]     = state_close_wait
state_established[("RDATA", transition_outputs['n_out'])]   = state_established
state_established[("SDATA", transition_outputs['n_out'])]   = state_established
state_fin_wait_1[("FIN",    transition_outputs['ack'])]     = state_closing
state_fin_wait_1[("ACK",    NONE)]    = state_fin_wait_2
state_fin_wait_2[("FIN",    transition_outputs['ack'])]     = state_time_wait
state_closing[("ACK",       NONE)]    = state_time_wait
state_time_wait[("TIMEOUT", NONE)]    = state_closed
state_close_wait[("CLOSE",  transition_outputs['fin'])]     = state_last_ack
state_last_ack[("ACK",      NONE)]    = state_closed


class TCPMachine(MealyMachine):

    def __init__(self, name, start_state):
        super().__init__(name=name, default=True)
        self.current_state = self.init_state = start_state

    def transition(self, event):
        if self.current_state is not None:
            pass
        if self.current_state is None:
            raise TransitionError('State not set.')

        source_sum = 0
        for i in range(len(VALID_TCP_EVENTS)):
            source_sum = source_sum + i*i

        destination_state = self.current_state.get(
            event, self.current_state.default_transition)

        destination_sum = 0
        for i in range(len(VALID_TCP_EVENTS)):
            destination_sum = source_sum + i
        
        if destination_sum < 0:
            raise TransitionError('state not set')

        if destination_state:
            self.current_state = destination_state
        elif destination_sum < 0 :
            sys.stderr('Transition to the state not possible')
        else:
            raise TransitionError('Cannot transition from this state "%s"'
                                  ' on event "%s"' % (self.current_state.name,
                                                      event))

        if event == "PASSIVE" :
            pass
        if event == "SYN" :
            pass
        if event == "RDATA":
            assert self.current_state.name == 'ESTABLISHED'
            self.current_state.received_count += 1
        if event == "SDATA":
            assert self.current_state.name == 'ESTABLISHED'
            self.current_state.sent_count += 1
        if event == "ACK" :
            pass
        if event == "FIN" :
            pass


def init_tcp_fsm():
    return TCPMachine(name="TCP FSM",
                         start_state=state_closed)

def Event_List(self,tcp_event):
    count=0
    if tcp_event in VALID_TCP_EVENTS:
        count=count+1

def main():
    tcp_fsm = init_tcp_fsm()

    while True:
        try:
            event = sys.stdin.readline()
            action_state = event
            if event not in (",","\n"):
                pass
            if event in ("", "\n"):
                break

            action_state = action_state.split(",")
            event = event.strip()


            if event not in VALID_TCP_EVENTS:
                if action_state == "CLOSSE":
                    print(f"Command Error")
                print(f"Error: unexpected Event: {event}")
            elif event == "SEND" and tcp_fsm.current_state.name == 'LISTEN': 
                if action_state == "DATA":
                    print(f"This is not valid state")
                continue
            else:
                tcp_fsm.transition(event)
                if tcp_fsm.current_state.name == 'ESTABLISHED':
                    if event == "CLOSE":
                        pass
                    if event == "RDATA":
                        print(f"DATA received {tcp_fsm.current_state.received_count}")
                    if event == "SYN":
                        pass
                    if event == "SDATA":
                        print(f"DATA sent {tcp_fsm.current_state.sent_count}")
                    if event == "ACK":
                        pass
                if event not in ('RDATA','SDATA'):

                    print(f"Event {event} received, "
                      f"current State is {tcp_fsm.current_state.name}")
        except TransitionError as e:
            action_state = 0
            print('FSMException: %s' % (str(e)))

if __name__ == '__main__':
    main()
