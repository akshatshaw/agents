#!/usr/bin/env python
import time
from typing import List

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from email_class import Email
from email_util import check_email, format_emails

from email_filter_crew import EmailFilterCrew


class AutoResponderState(BaseModel):
    emails: List[Email] = []
    checked_emails_ids: set[str] = set()


class EmailAutoResponderFlow(Flow[AutoResponderState]):
    initial_state = AutoResponderState

    @start("wait_next_run")
    def fetch_new_emails(self):
        print("Kickoff the Email Filter Crew")
        new_emails, updated_checked_email_ids = check_email(
            checked_emails_ids=self.state.checked_emails_ids
        )

        self.state.emails = new_emails
        self.state.checked_emails_ids = updated_checked_email_ids

    @listen(fetch_new_emails)
    def generate_draft_responses(self):
        print("Current email queue: ", len(self.state.emails))
        if len(self.state.emails) > 0:
            print("Writing New emails")
            emails = format_emails(self.state.emails)

            EmailFilterCrew().crew().kickoff(inputs={"emails": emails})

            self.state.emails = []

        print("Waiting for 10 seconds")
        time.sleep(10)


def kickoff():
    """
    Run the flow.
    """
    email_auto_response_flow = EmailAutoResponderFlow()
    email_auto_response_flow.kickoff()


def plot_flow():
    """
    Plot the flow.
    """
    email_auto_response_flow = EmailAutoResponderFlow()
    email_auto_response_flow.plot()


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    kickoff()
