import json
from urllib.parse import quote
from urllib.request import Request, urlopen

from experiments.github_api.fetch_pr import MakePRdata


def fetch_file_content(repo: str, commit_sha: str, file_path: str) -> str:
    encoded_path = quote(file_path, safe="/")

    file_url = (
        f"https://api.github.com/repos/{repo}"
        f"/contents/{encoded_path}?ref={commit_sha}"
    )

    request = Request(
        file_url,
        headers={
            "Accept": "application/vnd.github.raw+json",
            "User-Agent": "PR-Analyzer",
        },
    )

    with urlopen(request, timeout=15) as response:
        return response.read().decode("utf-8")


def get_merge_base(base_repo: str, base_sha: str, head_sha: str) -> str:
    compare_url = (
        f"https://api.github.com/repos/{base_repo}"
        f"/compare/{base_sha}...{head_sha}"
    )

    request = Request(
        compare_url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "PR-Analyzer",
        },
    )

    with urlopen(request, timeout=15) as response:
        comparison = json.loads(response.read().decode("utf-8"))

    return comparison["merge_base_commit"]["sha"]


def get_old_code(
    base_repo: str,
    merge_base_sha: str,
    changed_file: dict,
) -> str | None:
    # An added file has no earlier version.
    if changed_file["status"] == "added":
        return None

    # Renamed files must be fetched using their earlier path.
    old_path = changed_file.get(
        "previous_filename",
        changed_file["filename"],
    )

    return fetch_file_content(base_repo, merge_base_sha, old_path)


def get_new_code(
    head_repo: str,
    head_sha: str,
    changed_file: dict,
) -> str | None:
    # A removed file has no updated version.
    if changed_file["status"] == "removed":
        return None

    return fetch_file_content(
        head_repo,
        head_sha,
        changed_file["filename"],
    )


def main():
    pr_data = MakePRdata.getPRData()
    changed_files = MakePRdata.getChangedFiles()

    if pr_data is None or changed_files is None:
        print("Could not fetch the PR metadata or changed files.")
        return

    head_repository = pr_data["head"]["repo"]

    if head_repository is None:
        print("The PR's head repository is unavailable.")
        return

    head_repo = head_repository["full_name"]
    head_sha = pr_data["head"]["sha"]

    base_repo = pr_data["base"]["repo"]["full_name"]
    base_sha = pr_data["base"]["sha"]

    merge_base_sha = get_merge_base(base_repo, base_sha, head_sha)
    head_includes_target = merge_base_sha == base_sha

    print("Head repository:", head_repo)
    print("Head commit:", head_sha)
    print("Base repository:", base_repo)
    print("Base commit:", base_sha)
    print("Merge-base commit:", merge_base_sha)
    print("Head includes target:", head_includes_target)

    context = []

    for changed_file in changed_files:
        old_code = get_old_code(base_repo, merge_base_sha, changed_file)
        new_code = get_new_code(head_repo, head_sha, changed_file)

        old_path = changed_file.get(
            "previous_filename",
            changed_file["filename"],
        )

        context.append({
            "status": changed_file["status"],
            "old_path": (
                None if changed_file["status"] == "added" else old_path
            ),
            "new_path": (
                None
                if changed_file["status"] == "removed"
                else changed_file["filename"]
            ),
            "old_code": old_code,
            "new_code": new_code,
        })

    for item in context:
        print(f"\nFile: {item['new_path'] or item['old_path']}")
        print("Status:", item["status"])

        old_length = (
            len(item["old_code"])
            if item["old_code"] is not None
            else "not applicable"
        )
        new_length = (
            len(item["new_code"])
            if item["new_code"] is not None
            else "not applicable"
        )

        print("Before characters:", old_length)
        print("After characters:", new_length)


if __name__ == "__main__":
    main()