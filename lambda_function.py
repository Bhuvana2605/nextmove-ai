from agent.career_agent import CareerAgent


def lambda_handler(event, context):
    try:
        agent = CareerAgent()
        agent.run()

        return {
            "statusCode": 200,
            "body": "NextMove AI executed successfully."
        }

    except Exception as e:
        print(f"Lambda Error: {e}")

        return {
            "statusCode": 500,
            "body": str(e)
        }