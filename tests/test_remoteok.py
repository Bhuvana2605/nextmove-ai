from providers.remoteok import RemoteOKProvider

provider = RemoteOKProvider()

jobs = provider.fetch()

print(f"Fetched {len(jobs)} jobs\n")

for job in jobs[:5]:
    print("=" * 60)
    print("Title:", job.title)
    print("Repository:", job.repository)
    print("URL:", job.url)
    print("Language:", job.language)
    print("Tags:", job.tags)
    print("Description:", job.description[:200])
    print()