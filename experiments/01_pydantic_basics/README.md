# Experiment 01: Pydantic basics

This is a learning experiment, not the analyzer's final input/output contract.

## What I tried

- Define required string fields with a Pydantic model.
- Validate an external Python dictionary with `model_validate()`.
- Pass an integer where a string is expected and inspect the validation error.
- Validate handwritten JSON review output with `model_validate_json()`.
- Access fields on the resulting Python object.

## What failed and what I learned

- Dictionary keys must match model field names exactly, including capitalization and whitespace.
- Creating the input model with no values fails because its fields are required.
- An integer is not accepted for the string field under the current default validation.
- An uncaught validation error stops execution before later print statements.
- Catching the error lets the experiment continue; the input trial currently uses a broad `Exception` catch while the output trial catches `ValidationError` specifically.
- Successful validation checks structure and types, not the truth of an LLM's reasoning.

## Run

From the repository root, after installing `requirements.txt`:

```powershell
.\.venv\Scripts\python.exe experiments/01_pydantic_basics/demo.py
```

Expected output: the first input object, a handled validation error for the second input, then the example review summary and concerns.

The JSON response is handwritten. This experiment does not call an LLM.
