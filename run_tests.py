#!/usr/bin/env python3
import unittest
import sys
import os

def print_test_summary(result):
    """Print a summary of the test results"""
    print("\n=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    # Calculate success rate
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"Success rate: {success_rate:.2f}%")
    
    # Print coverage information
    print("\n=== Test Coverage ===")
    print("Modules tested:")
    print("- sovits.utils: Basic text processing utilities")
    print("- inference.inference: Core TTS inference functionality")
    print("- api: FastAPI endpoints for TTS service")
    
    print("\nModules not covered:")
    print("- sovits.models: Neural network model definitions")
    print("- sovits.process: Audio processing pipeline")
    print("- inference.inference_llama: LLM inference implementations")
    print("- data_process: Data preprocessing utilities")
    
    print("\nNote: Full coverage would require setting up the TTS models and dependencies.")

if __name__ == "__main__":
    # Discover and run all tests in the tests directory
    test_suite = unittest.defaultTestLoader.discover('tests')
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Print summary
    print_test_summary(result)
    
    # Return non-zero exit code if tests failed
    sys.exit(not result.wasSuccessful())