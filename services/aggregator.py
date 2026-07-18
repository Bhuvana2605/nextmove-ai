from models.opportunity import Opportunity


class Aggregator:

    def merge(self, opportunities: list[Opportunity]) -> list[Opportunity]:
        """
        Remove duplicates and preserve the strongest opportunities per source.
        """

        filtered = []
        seen_keys = {}
        github_count = 0
        remoteok_count = 0

        for opportunity in opportunities:
            if not opportunity:
                continue

            url = (getattr(opportunity, "url", "") or "").strip().lower()
            title = (getattr(opportunity, "title", "") or "").strip().lower()
            repository = (getattr(opportunity, "repository", "") or "").strip().lower()

            matched_index = None
            for key_value in (url, title, repository):
                if key_value and key_value in seen_keys:
                    matched_index = seen_keys[key_value]
                    break

            if matched_index is not None:
                existing = filtered[matched_index]
                if getattr(opportunity, "quality_score", 0) > getattr(existing, "quality_score", 0):
                    filtered[matched_index] = opportunity
                continue

            if getattr(opportunity, "source", "") == "GitHub":
                if github_count >= 10:
                    continue
                github_count += 1
            elif getattr(opportunity, "source", "") == "RemoteOK":
                if remoteok_count >= 10:
                    continue
                remoteok_count += 1

            filtered.append(opportunity)
            index = len(filtered) - 1

            if url:
                seen_keys[url] = index
            if title:
                seen_keys[title] = index
            if repository:
                seen_keys[repository] = index

        return filtered