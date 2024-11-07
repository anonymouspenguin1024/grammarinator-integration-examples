# Grammarinator Integration Examples

This repository provides examples of how to integrate **[Grammarinator](https://github.com/renatahodovan/grammarinator)** with various fuzzing frameworks. Currently, it demonstrates the integration of **Grammarinator** and **[Fuzzinator](https://github.com/renatahodovan/fuzzinator)**, showcasing multiple use cases and configurations.

## Scenarios

The repository includes the following three scenarios, highlighting different ways to utilize grammar-based fuzzing:

1. **Batch Execution via CLI**
   Fuzzinator iteratively executes Grammarator's **command-line interface (CLI)** to generate batches of test cases. These test cases are then evaluated using Fuzzinator.

2. **Batch Execution via API**
   Instead of using Grammarinator's CLI, Fuzzinator integrates directly with Grammarinator's **Python API** to generate and evaluate test cases.

3. **Coverage-Guided Fuzzing**
   The basic Grammarinator API configuration is extended with **coverage guidance** to focus fuzzing efforts on exploring new code paths.


## Structure

- **`fuzzinator/`**
  Contains the individual configurations and scripts for each scenario, organized into subfolders:
  - `cli/`: Batch execution using Grammarinator CLI.
  - `api/`: Batch execution using Grammarinator API.
  - `guided/`: Coverage-guided fuzzing setup.

- **`resources/`**
  Contains all downloaded or generated resources, such as the **[JerryScript](https://github.com/jerryscript-project/jerryscript) target** or the Generators produced from grammars.

- **`setup.sh`**
  A script to automate the setup process, including downloading and building the required components.

## Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/renatahodovan/grammarinator-integration-examples.git
   cd grammarinator-integration-examples
   ```

2. Run `setup.sh` to prepare the environment and enter the created virtual environment:
    ```bash
   ./setup.sh && source .venv/bin/activate
   ```

3. Navigate to the desired scenario directory (e.g., `fuzzinator/cli/`) and execute `run.sh`.

## Requirements

- git
- Python 3
- virtualenv
- Java
- cmake, make
