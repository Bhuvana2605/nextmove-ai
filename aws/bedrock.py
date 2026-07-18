import boto3

client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

MODEL_ID = "amazon.nova-lite-v1:0"


def invoke(prompt: str) -> str:
    """
    Sends a prompt to Amazon Nova Lite and returns the text response.
    """

    response = client.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        inferenceConfig={
            "maxTokens": 1200,
            "temperature": 0.2,
            "topP": 0.9,
        }
    )

    content = response["output"]["message"]["content"]

    text = ""

    for block in content:
        if "text" in block:
            text += block["text"]

    return text.strip()