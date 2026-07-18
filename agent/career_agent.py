from providers.github import GitHubProvider
from providers.remoteok import RemoteOKProvider

from services.aggregator import Aggregator
from agent.brain import Brain

from aws.memory import MemoryStore
from aws.email_service import EmailService


class CareerAgent:

    USER_ID = "demo-user"

    def __init__(self):

        self.providers = [
            GitHubProvider(),
            RemoteOKProvider()
        ]

        self.aggregator = Aggregator()
        self.brain = Brain()
        self.memory = MemoryStore()
        self.email = EmailService()

    def run(self):

        print("\n🚀 NextMove AI Started...\n")

        opportunities = []
        provider_fetched = {}

        for provider in self.providers:
            print(f"Fetching from {provider.__class__.__name__}...")

            try:
                provider_opportunities = provider.fetch()
                provider_fetched[provider.__class__.__name__] = len(provider_opportunities)

                print(
                    f"✓ {provider.__class__.__name__} returned "
                    f"{len(provider_opportunities)} opportunities."
                )

                opportunities.extend(provider_opportunities)

            except Exception as exc:
                provider_fetched[provider.__class__.__name__] = 0
                print(
                    f"✗ Failed to fetch from {provider.__class__.__name__}: {exc}"
                )

        print(f"GitHub fetched: {provider_fetched.get('GitHubProvider', 0)}")
        print(f"RemoteOK fetched: {provider_fetched.get('RemoteOKProvider', 0)}")
        print(f"\nCollected {len(opportunities)} opportunities before merge.")

        before_merge = len(opportunities)
        opportunities = self.aggregator.merge(opportunities)
        print(f"Duplicates removed: {before_merge - len(opportunities)}")
        print(f"Collected {len(opportunities)} opportunities after merge.")

        opportunities = self.memory.filter_new(
            self.USER_ID,
            opportunities
        )
        print(f"Memory filtered: {len(opportunities)}")
        print(f"{len(opportunities)} new opportunities remain.\n")

        if not opportunities:
            print("No new opportunities available today.")
            return

        print(f"Sent to Nova: {len(opportunities)}")

        try:
            plan = self.brain.create_daily_plan(opportunities)
        except Exception as exc:
            print(f"Bedrock Error: {exc}")
            plan = None

        if plan is None:
            return

        print("=" * 60)
        print("🎯 TODAY'S MISSION")
        print("=" * 60)

        print(f"\nMission Score: {plan.mission_score}\n")
        print(plan.summary)
        print()

        saved_count = 0
        for item in plan.schedule:
            print(f"{item.priority}. {item.title}")
            print(f"Action      : {item.action}")
            print(f"Reason      : {item.reason}")
            print(f"Why         : {item.why_selected}")
            print(f"Confidence  : {item.confidence}")
            print(f"Time        : {item.estimated_minutes} mins")
            print(f"URL         : {item.url}")
            print()

            matching_opportunity = None
            for opportunity in opportunities:
                if getattr(opportunity, "id", "") == str(getattr(item, "opportunity_id", "")):
                    matching_opportunity = opportunity
                    break

            if matching_opportunity is None:
                continue

            try:
                self.memory.save_recommendation(
                    self.USER_ID,
                    matching_opportunity
                )
                saved_count += 1
            except Exception as exc:
                print(f"Memory Error: {exc}")

        print(f"Recommendations saved: {saved_count}")
        print(f"Total Time : {plan.total_effort_minutes} mins")
        print(f"Remaining  : {plan.remaining_minutes} mins")

        success = self.email.send_daily_plan(plan)

        if success:
            print("✓ Daily email sent successfully.")
        else:
            print("✗ Failed to send daily email.")