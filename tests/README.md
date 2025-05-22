# Muyan-TTS Tests

This directory contains unit tests for the Muyan-TTS project.

## Test Structure

The tests are organized by module:

- `test_text_utils.py`: Tests for text processing utilities
- `test_api.py`: Tests for the FastAPI endpoints
- `test_inference.py`: Tests for the TTS inference functionality

## Running Tests

To run all tests:

```bash
python run_tests.py
```

To run a specific test file:

```bash
python -m unittest tests/test_text_utils.py
```

## Dependencies

The tests require the following dependencies:

- Python 3.8+
- PyTorch
- librosa
- fastapi
- uvicorn
- numpy
- soundfile
- ffmpeg-python

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Test Coverage

Current test coverage:

- `sovits.utils`: Basic text processing utilities
- `inference.inference`: Core TTS inference functionality
- `api`: FastAPI endpoints for TTS service

Modules not covered by tests:

- `sovits.models`: Neural network model definitions
- `sovits.process`: Audio processing pipeline
- `inference.inference_llama`: LLM inference implementations
- `data_process`: Data preprocessing utilities

## Adding New Tests

When adding new tests:

1. Follow the existing test structure
2. Use descriptive test method names
3. Add docstrings to explain what each test is checking
4. Use unittest.mock to mock external dependencies when possible

## Mock Implementation

Some tests use mock implementations of the original functions to avoid dependencies. This allows testing the logic without requiring the full TTS model setup.