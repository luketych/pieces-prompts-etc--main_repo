- - ## Using backlog.md for Task Management
  
    
  
    Tasks are organized inside the `backlog/tasks/` directory. To create or update tasks:
  
    - **Locate the Board:** Find your task board in `backlog/tasks/`.
    - **Create or Edit Tasks:** Add new task files or edit existing ones.
  
    ------    
  
    ## Workflow Status Columns  
    
  
    Each task moves through status columns. Common default columns include:
  
    **To Do → In Progress → Done**
  
    Other boards may use variations like:
  
    - **Todo → Doing → Review → Done**
    - **To Do → In Progress → Waiting For Review → Done**
  
    **Important:**
  
    - When starting a task, move it from **To Do** (or equivalent) to **In Progress** (or **Doing**).
    - When finishing a task, don’t move it straight to **Done** if a **Review** (or **Waiting For Review**) column exists. Move it to the appropriate intermediate step first.
    - **Note that in the `backlog` folder there might be a directory called "completed". When tasks are completed do not move them there. Instead just update the task's status to "Done".**
  
    ------

    ## Example Card to demonstrate format

    ---
    id: task-001
    title: "Data Pipeline Setup & yfinance Integration"
    status: "Done"
    assignee: []
    created_date: '2025-01-18'
    labels: ["data", "yfinance", "foundation", "core"]
    dependencies: []
    milestone: "milestone-1--foundation-core-scoring-engine"
    ---

    ------
  
    ## Self-State Checks

    Before starting a new task decide at least several points in your implemention process when you will check the .md file for the task throughout implementing it. For example, you will need to update sub-tasks, check them off as they are completed.

    You will also need to pick at least several points to perform your reflections (see backlogmd_reflection_points.md).

    ------

    ## After finishing a task (changing a task's status to either Done or Review)

    - The top of a commit message should assume the reader wants to quickly and easily (with minimal mental effort) understand what was being worked on, why, and how. Then as the commit message is being written you can get more detailed after an initial skeleton has been presented to the reader. Leave nuances, and good-to-know details at the bottom of the commit message. Similar to an encyclopedia or science book you can use asterisks in the commit messages, with reference to the detailed explanation down at the bottom of the commit message.
    - write a detailed commit message about what was completed since the previous commit. Mention the task name and reference it when describing the parts of the task that have been co
mpleted in the commit message. If multiple tasks have been completed since the last commit then make sure to make this explicit in the commit message and have sub-sections for each task. If a task was mostly completed but some issues remain or some subtasks have not been completed mention that towards the end of the commit message.
    - similarly, add details on milestones and sprints that were being worked on in the commit message, and be explicit about the names and reference to where the reader can find more information. Mention how what was being worked on aligns with each task, milestone, sprint that was being worked on.
    - If no tasks, milestones or sprints were being worked on in the commit then mention that near the top of the commit message.
    - the commit message should start with a concise description of what was completed since the last commit, including mention of what tasks, milestones, sprints were being worked on.


    ------

    ## Example Task: Secure Path Validation Utilities
    
  
    ### Description
  
    
  
    Implement secure path validation utilities to prevent path traversal attacks and handle filesystem edge cases. This is the security foundation for all other filesystem operations.
  
    
  
    ### Dependencies
  
    
  
    None (foundation component)
  
    
  
    ### What "Done" Looks Like
  
    
  
    - **Good Enough:** Basic path sanitization blocking obvious traversal attempts.
    - **Done:** Comprehensive validation including:
      - Symlink detection
      - Permission checks
      - Circular reference prevention
      - Cross-platform normalization
  
    
  
    ### Potential Side Effects
  
    
  
    - **Performance Impact:** Slight overhead on all file operations.
    - **False Positives:** Risk of blocking valid paths.
    - **Platform Differences:** Inconsistent behavior on Windows vs. Unix.
    - **Symlink Complexity:** May cause subtle and unexpected issues.
  
    
  
    ### How to Measure Completion
  
    
  
    - **✅ Security:** 100% pass on known path traversal vectors (`../../../etc/passwd`, `..\..\windows\system32`)
    - **✅ Edge Cases:** Validates 20+ edge cases (long paths, Unicode, special characters)
    - **✅ Performance:** Adds <1ms per check
    - **✅ Cross-Platform:** Passes on Windows, macOS, and Linux
  
    
  
    ### Testing Strategy
  
    
  
    
  
    #### Unit Tests (TDD Approach)
  
    
  
    TypeScript
  
    ```
    // test/unit/PathValidator.test.ts
    
    describe('Path Sanitization', () => {
      test('blocks path traversal attacks', () => {
        expect(sanitizePath('../../../etc/passwd')).toThrow('Invalid path');
        expect(sanitizePath('..\\..\\windows\\system32')).toThrow('Invalid path');
      });
    
      test('handles unicode and special characters', () => {
        expect(sanitizePath('/valid/path/with_émojis_🚀')).toBeTruthy();
        expect(sanitizePath('/path with spaces')).toBeTruthy();
      });
    
      test('detects circular symlinks', () => {
        // Test using symlinked directories in test_resources
      });
    });
    ```
  
    
  
    #### Integration Points
  
    
  
    - **File Scanner:** All scanned paths validated
    - **Database:** Store only validated, normalized paths
    - **API Endpoints:** Validate all user-provided paths before use
  
    
  
    #### Anti-Ice Cream Measures
  
    
  
    - **🧪 70% Unit Tests:** Focus on core functions (`sanitizePath`, `normalizePath`, `validateDepth`)
    - **🔌 20% Integration Tests:** Cover interactions with filesystem APIs
    - **🌐 10% E2E Tests:** Full pipeline from input to validation
    - **⚡ Fast Feedback:** Keep unit test runtime <10ms
    - **🚫 Avoid Over-Integration:** Don’t duplicate unit logic in slow tests
  
    ------
  
    
  
    ## Task Design Guidelines
  
    
  
    Every task should address the following:
  
    - **Concise Description:**
      - What is being done, where, why, and how.
      - Include likely file changes and integration points.
    - **Definition of Done:**
      - Define both “good enough” and “done.”
      - Include measurable outcomes and completion criteria.
    - **Potential Side Effects:**
      - Identify risks, performance hits, or platform quirks.
    - **Testing Strategy:**
      - Outline what, when, where, why, and how.
      - Include unit, integration, and E2E coverage balance.
    - **Milestones:**
      - Clearly state the milestone the task supports.
      - This ensures alignment with overall design goals and prevents deviation from milestone intent.
