from typing import *
from pydantic import *

class reviewOutput(BaseModel):
    summary : str = Field(min_length=1)
    assessment : Literal['concern found','no concern found','insufficient context']
    concerns : list[str] = Field(default_factory=list)


if __name__ == "__main__":
    llm_response_1 = '''
        {
            "summary" : "I have understood the whole code",
            "assessment" : "concern found"
        }
     '''
    llm_response_2 = '''
             {
                 "summary" : "I have understood the whole code",
                 "assessment" : "concern not found",
                 "concerns" :   ["Concern 1", "Concern 2","Concern 3"]
             }
          '''

    try:
        validate_resp_1 = reviewOutput.model_validate_json(llm_response_1)
        print(validate_resp_1)
    except Exception as e:
        print(e)

    try:
        validate_resp_2= reviewOutput.model_validate_json(llm_response_2)
        print(validate_resp_2)
    except Exception as e:
        print(e)
