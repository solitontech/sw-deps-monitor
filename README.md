# hawkeye

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./License)

[![Author](https://img.shields.io/badge/Author-Karthick%20Shanmuga%20Rao-blue)](https://github.com/karthickshanmugarao)

This repository contains a suite of tools to monitor software library dependencies, prevent undesirable coupling, and maintain a clean and structured codebase. The tools are designed to be integrated into the CI/CD pipeline to provide continuous feedback on the architectural health of the software project.

## Vision
*   Maintain architectural integrity and promote modular design by enforcing strict dependency rules across the codebase.
*   Empower development teams with a fully automated system for monitoring and enforcing dependency rules.
*   Integrate directly into the CI/CD pipeline to catch architectural deviations early.
*   Prevent technical debt, reduce complexity, and ensure the software design remains robust and scalable over time.
*   Enable Guided changes to the software design by providing a clear process for introducing new dependencies, ensuring that all changes are intentional and aligned with the overall architecture.
*   Provide actionable insights and visualizations to help architects and developers understand and manage dependencies effectively.

## How It Works

Architects and Tech Leads can define the expected dependencies for each library and orphan class in .hawkeye files. The Tools with CICD setup can ensure that the developers adhere to the defined dependencies during the development process. This ensures adherence to the defined design and helps maintain the separation of concerns through automation.

If Developers accidentally introduce an unexpected dependency, the tools can catch it and report it in the pull request reviews, and block the merge to the main branch until the issue is resolved.

If Developers see a need to introduce a new dependency, they can align with the Leads/Architects to seek their guidance and approval and then update the .hawkeye files accordingly to introduce the change in design. 

At any point in time, the ActualDepsList.hawkeyelist file can be reviewed by the Architects and Tech Leads to find if the dependencies are as expected in the repository. They can also visualize the dependencies by generating a graph image output from the ActualDepsList.hawkeyelist file to get a better understanding of the dependencies between the libraries in the repository. This can help them identify any potential issues with the dependencies and take necessary actions to resolve them.

<u>**More Details in the presentation:**</u> 
[Automated Dependency Monitoring in CI Pipeline](Docs/Automated%20Dependency%20Monitoring%20in%20CI%20Pipeline.pptx)

## Key Features
*   **Dependency Validation:** Automatically compare actual project dependencies against a predefined set of expected dependencies and flag any violations.
*   **Circular Dependency Detection:** Scan the entire dependency graph to identify and report any circular references between modules, which can hinder modular builds and testing.
*   **Pull Request Integration:** Intelligently analyze only the files changed in a pull request, providing fast, targeted feedback to developers.
*   **CI/CD Native:** Seamlessly integrates with CI/CD workflows (e.g., GitHub Actions) to automate checks and enforce architectural rules on every change.
*   **Architectural Health Metrics:** Calculate and report key software metrics, including Afferent Coupling (Ca), Efferent Coupling (Ce), and Instability (I), to provide quantitative insights into the codebase's structure.
*   **Advanced Graph Visualization:** Generate clear, hierarchical dependency graphs for the entire repository or for specific modules, making complex relationships easy to understand.
*   **Scheduled Everday Dependency Audits:** Automatically run comprehensive dependency checks on a regular schedule (e.g., daily) to ensure ongoing compliance with architectural standards and catch issues early.
*   **Customizable Reporting:** Generate detailed reports in multiple formats, including console output, PNG images for graphs, and structured Markdown files.


## Types of Automated Checks

| # | Check Type | Workflow File | Description |
|:--|:---|:---|:---|
| 1 | **Check Modified Libraries Only** | `DependenciesCheckModifiedLibraries.yml` | Performs checks only on libraries modified in the current branch. Used in Pull Requests to block merges if unexpected or circular dependencies are introduced. |
| 2 | **Check All Libraries** | `DependenciesCheckAllLibraries.yml` | Performs checks on all libraries in the repository. Scheduled to run at regular intervals (e.g., daily) to continuously monitor the entire repository. |

## Available Tools

| # | Tool | Description |
|:--|:---|:---|
| 1 | `scripts/generate_changed_files_list.py` | Finds the list of changed files and libraries in the current branch and saves the details. This is useful for pull request reviews to perform automated checks only on the libraries that are edited in the current branch. |
| 2 | `CICD/AutomatedChecks/UnexpectedDepsCheck.vi` | Compares the expected dependencies (defined in `.hawkeye` files) with the actual dependencies (read from `.lvproj` files) and reports any unexpected dependencies. It can be configured to check only modified libraries. |
| 3 | `CICD/AutomatedChecks/UpdateActualDepsList.vi` | Updates the `ActualDepsList.hawkeyelist` file with the current actual dependencies. It can be configured to update only the sections corresponding to modified libraries. |
| 4 | `scripts/find_circular_paths.py` | Finds and reports circular dependency paths from the `ActualDepsList.hawkeyelist` file. |
| 5 | `scripts/generate_full_dependency_graph.py` | Generates a full dependency graph image from `ActualDepsList.hawkeyelist` to visualize dependencies between all libraries. |
| 6 | `scripts/generate_dependency_graph_for_selected_nodes.py` | Generates a dependency graph image for specified nodes/libraries. |
| 7 | `scripts/find_root_nodes.py` | Finds and reports root nodes (libraries with no incoming dependencies). This is useful for identifying top-level libraries for complete project rebuilds. |
| 8 | `scripts/sort_actual_deps_list.py` | Sorts the `ActualDepsList.hawkeyelist` file alphabetically, making it easier to read and compare in pull request reviews. |
| 9 | `scripts/calculate_coupling_metrics.py` | Calculates Afferent Coupling (Ca), Efferent Coupling (Ce), and Instability (I) for each module. It provides a console table and a markdown report, which are useful for assessing architectural health. |

