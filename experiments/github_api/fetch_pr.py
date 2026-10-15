import json
from urllib.error import *
from urllib.request import *
from pydantic import ValidationError
from experiments.Checking_PRs.exploring_json import PullRequestInput


class MakePRdata:
    
    url_1 = "https://api.github.com/repos/spring-projects/spring-petclinic/pulls/2663"
    url_2 = "https://api.github.com/repos/spring-projects/spring-petclinic/pulls/2663/files"


    def getPRData() -> list | None:
        url_1 = "https://api.github.com/repos/spring-projects/spring-petclinic/pulls/2663"
        request = Request(url_1)
        request.add_header("Accept", "application/vnd.github+json")
        request.add_header("User-Agent", "PR-Analyzer")   
        try:
                with urlopen(request, timeout= 15) as response:
                    return json.loads(response.read().decode('utf-8'))
        except HTTPError as e:
            print(f"HTTP Error: {e.code} {e.reason}")
        except URLError as e:
            print(f"URL Error: {e.reason}")
    
    def getChangedFiles() -> list | None:
            url_2 = "https://api.github.com/repos/spring-projects/spring-petclinic/pulls/2663/files"
            request = Request(url_2)
            request.add_header("Accept", "application/vnd.github+json")
            request.add_header("User-Agent", "PR-Analyzer")   
            try:
                    with urlopen(request, timeout= 15) as response:
                        return json.loads(response.read().decode('utf-8'))
            except HTTPError as e:
                print(f"HTTP Error: {e.code} {e.reason}")
            except URLError as e:
                print(f"URL Error: {e.reason}") 
    
    def build_review_json(pr_data: dict, changed_files_data: list) -> str:
        changed_files_list = []

        for item in changed_files_data:
            changed_files_list.append({
                "path": item["filename"],
                "patch": item.get("patch"),
            })

        data = {
            "pr_url": pr_data["html_url"],
            "title": pr_data["title"],
            "description": pr_data["body"],
            "changed_files": changed_files_list,
        }

        validated_pr = PullRequestInput.model_validate(data)
        return validated_pr.model_dump_json(indent=2)

        # return json.dumps(data, indent=2)
        

if __name__ == "__main__":
    
    pr_data = MakePRdata.getPRData()
    changed_files_data = MakePRdata.getChangedFiles()
    
    if pr_data is not None and changed_files_data is not None:
        review_json = MakePRdata.build_review_json(
            pr_data, changed_files_data
        )
    print(review_json)
    
    
    # --mock test--
    # test_pr = {
    #     "html_url": "https://github.com/example/project/pull/1",
    #     "title": "Prevent duplicate payments",
    #     "body": "Reject payment for already-paid orders.",
    # }

    # test_files = [
    #     {
    #         "filename": "PaymentService.java",
    #         "patch": 123,  # Deliberately invalid
    #     }
    # ]

    # try:
    #     result = MakePRdata.build_review_json(test_pr, test_files)
    #     print(result)
    # except ValidationError as error:
    #     print(error)
    # -------------
    
    
    
    
    
    