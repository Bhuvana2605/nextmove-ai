from aws.bedrock import invoke

print(
    invoke(
        "Reply with only the word SUCCESS."
    )
)