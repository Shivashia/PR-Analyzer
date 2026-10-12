import json
from pathlib import Path
from pydantic import BaseModel, Field

class ChangedFile(BaseModel):
    path : str = Field(min_length=1)
    patch : str


class PullRequestInput(BaseModel):
    pr_url : str
    title : str
    description : str
    changed_files: list[ChangedFile]


if __name__ == "__main__":

    path = Path(__file__).with_name("pr_sample.json")
    with path.open(encoding="utf-8") as file:
        try:
            pr_data = json.load(file)
        except json.JSONDecodeError as e:
            print(e)
            raise SystemExit(1)

    # print(pr_data["pr_url"])
    # print(print(pr_data["changed_files"]))

    for items in pr_data["changed_files"]:
        try:
            fileValidator = ChangedFile.model_validate(items)
            print(fileValidator)
        except Exception as e:
            print(e)

    try:
        pr_validate = PullRequestInput.model_validate(pr_data)
        # print(pr_validate.title)
        # print(pr_validate.changed_files[0].path)
    except Exception as e:
        print(e)

    # print(type(pr_data["changed_files"][0]))
    # print(type(pr_validate.changed_files[0]))
