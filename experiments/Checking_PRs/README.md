# PR input validation and code context

This folder contains learning experiments for the PR analyzer. `exploring_json.py` explores Pydantic validation of PR input. `contextFetching.py` retrieves the full before and after versions of files changed by a PR.

A patch shows which lines changed. Full source files let a reviewer inspect the surrounding implementation as well. Collecting both versions gives us evidence to compare; deciding which parts to send to the LLM is a later step.

## Run the context experiment

From the repository root, with the project's virtual environment activated:

```powershell
python -m experiments.Checking_PRs.contextFetching
```

Run it as a module so imports from `experiments.github_api` resolve. It uses `MakePRdata` from `../github_api/fetch_pr.py`, which currently targets [Spring Petclinic PR #2663](https://github.com/spring-projects/spring-petclinic/pull/2663). There is no command-line PR selector yet. Importing the fetcher does not run its guarded script section or rewrite its JSON output.

The context script makes public GitHub API requests. It does not need a Gemini key, call an LLM, or run the Java application. Install the repository's Python requirements in the virtual environment first; importing the existing fetcher also imports its Pydantic models.

## Repositories, branches, and commits

| Term | Meaning |
| --- | --- |
| Base repository | Repository receiving the PR |
| Base branch | Target branch, such as `dev` or `main` |
| Base SHA | Target commit recorded in the fetched PR response |
| Head repository | Repository containing the proposed changes; it may be a fork |
| Head SHA | Exact proposed commit whose updated files we fetch |
| Merge-base SHA | Common ancestor returned by comparing the base and head commits |

A repository contains branches. A branch points to a commit. A fork is a separate repository connected to the original project.

```text
A--B--C--D       target/dev
    \
     E--F       feature branch
```

Here D is the target snapshot, F is the proposed commit, and B is their merge base. Comparing B with F isolates the feature branch's changes. The PR still proposes merging into the target at D, not into B. Git uses the shared history to combine changes; a successful merge does not prove functional correctness.

The script checks `merge_base_sha == base_sha`. If true, the head includes that target commit in its ancestry. If false, the target has commits the head has not incorporated. Neither result is a code-quality verdict. These values describe the fetched snapshot, not a target branch that might advance afterward. A merged PR's recorded base SHA should not be treated as today's default-branch tip.

## Retrieval flow

1. Fetch PR metadata and the changed-files list through the existing fetcher.
2. Read the head/base repositories and commit SHAs.
3. Compare the commits through GitHub's API to obtain `merge_base_commit.sha`.
4. For each changed file, fetch its before version at the merge base and its after version at the head.
5. Collect the contents in memory and print paths, statuses, and character counts.

| Function | Responsibility |
| --- | --- |
| `fetch_file_content()` | Fetch a UTF-8 source file at a specified commit; URL-encode its path |
| `get_merge_base()` | Request comparison metadata and return the common ancestor's SHA |
| `get_old_code()` | Select the earlier path/version, or return `None` for an added file |
| `get_new_code()` | Select the updated path/version, or return `None` for a removed file |
| `main()` | Coordinate requests, build the context list, and print a summary |

Comparison requests use `Accept: application/vnd.github+json` and parse the response with `json.loads()`. Source requests use `Accept: application/vnd.github.raw+json`, which returns the file text directly despite the media type's name. They do not need JSON parsing or Base64 decoding.

## Added, removed, and renamed files

| GitHub status | Before | After |
| --- | --- | --- |
| `modified` | Current path at merge base | Current path at head |
| `added` | `None` | Current path at head |
| `removed` | Current path at merge base | `None` |
| `renamed` | `previous_filename` at merge base | Current path at head |

Each context entry contains `status`, `old_path`, `new_path`, `old_code`, and `new_code`. `None` represents an inapplicable version, not a failed fetch. An empty file instead has an empty string. HTTP, network, and decoding errors currently propagate and stop the run.

## What has been checked

A manual run retrieved both versions of the two modified files in PR #2663:

| File | Before characters | After characters |
| --- | ---: | ---: |
| `Visit.java` | 1698 | 1760 |
| `VisitControllerTests.java` | 3815 | 4300 |

The head was `19d7601e9afb7f0e82effa9f739a162e8dc6384e`; the base and merge base were both `818c4136ea971c21674525f9053de0d9c7ad8cfe`. These are Python string character counts, not byte sizes, token counts, test results, or proof that the PR is correct. Added, removed, and renamed handling is implemented but was not exercised by this two-file run.

## Current limits and next steps

- Context is local to `main()` and disappears when the script exits. It is not yet validated, saved to `review_input.json`, or supplied to Gemini.
- Only changed files are collected. Related unchanged files, such as a controller using an entity, are not discovered automatically.
- Source is assumed to be UTF-8 text. Binary files, large files, submodules, and symlinks need explicit handling.
- The existing changed-files fetcher does not paginate. Large PRs can therefore produce an incomplete list.
- Metadata and file lists are fetched separately. An actively changing PR needs snapshot-consistency checks before this becomes a dependable collector.
- Requests have a 15-second timeout but no custom retry or rate-limit handling. An unavailable head repository stops collection.

Next, define a validated context structure that preserves commit provenance, then decide which collected evidence belongs in the model input. Fetching evidence and selecting model context are separate responsibilities.
