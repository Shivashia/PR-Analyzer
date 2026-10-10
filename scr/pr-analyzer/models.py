from pydantic import BaseModel, ValidationError

class input(BaseModel):
    commit_tag : str
    code_change : str

class ReviewOutput(BaseModel):
    summary: str
    concerns: list[str]
    
    
if __name__ == "__main__":
    
    external_data_1 = {'commit_tag' : "This is an exaple Commit_tag", 'code_change': "Random Code Change" }
    external_data_2 = {'commit_tag' : "This is an exaple Commit_tag", 'code_change': 123 }
    input_validate_1 = input.model_validate(external_data_1)
    print(input_validate_1)
    try:
        input_validate_2 = input.model_validate(external_data_2)
        print(input_validate_2)
    except Exception as e:
        print(type(e).__name__) 
        print(e)                  
        
    
    llm_response = '''
    {
        "summary": "The payment check happens after charging.",
        "concerns": ["An already-paid order reaches the charge call."]
    }
    '''
    try:
        report = ReviewOutput.model_validate_json(llm_response)
        print(report.summary)
        print(report.concerns)
    except ValidationError as error:
        print(error)